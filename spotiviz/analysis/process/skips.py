"""
The code in this file determines which listens will count as skips. This is
done by analyzing the TrackLengths table, where each row is a track-duration.
That is, each row contains a specific track and a duration (in milliseconds)
that that track was played. Tracks that were played multiple times often have
multiple entries, one for each of their lengths.

This code populates the `skip` column within that table with a flag to
indicate whether it is determined to be a skip.
"""
import enum
import sqlite3
from typing import Optional, List

import pandas as pd

from spotiviz.utils import db
from spotiviz.utils.log import LOG
from spotiviz.projects import utils as ut

# The minimum duration a track must play for in order for it not to be counted
# a skip (assuming no duration has a frequency of 2 or more). This is given
# in milliseconds.
MIN_TRACK_LENGTH = 10000

# If a duration has a frequency of at least MIN_FREQUENCY and makes up at least
# FREQUENCY_PERCENT_THRESHOLD percent of the listens for that track, it is
# marked a NON_SKIP.
MIN_FREQUENCY = 2

# See MIN_FREQUENCY
FREQUENCY_PERCENT_THRESHOLD = 0.1

# If a duration has a frequency of at least ABSOLUTE_NON_SKIP_FREQUENCY,
# it will always be marked NON_SKIP, regardless of what percentage of the
# total listens that this duration comprises.
ABSOLUTE_NON_SKIP_FREQUENCY = 6

# As long as a duration is within this percent less than another NON_SKIP
# duration, this one will also be marked NON_SKIP.
#
# For example, if one
# duration is 100 seconds, and it's marked NON_SKIP, then any duration of at
# least 98 seconds will also be marked NON_SKIP (at a 2% error margin).
SKIP_ERROR_MARGIN = 0.02


class SkipState(enum.Enum):
    """
    This represents whether an individual duration for a certain track is
    counted as a skip. It can either be a SKIP or NOT_SKIP. The value of each
    enum is how it will be stored in the SQLite database.
    """

    SKIP = 'S'
    NON_SKIP = 'N'


def determine_skips(project: str) -> None:
    """
    Go through each of the durations that each song was played for by iterating
    over the TrackLengths table.

    Precondition:
        The given project name MUST be valid, as it is not checked.

    Args:
        project: The name of the project (MUST be valid--not checked).

    Returns:
        None
    """

    LOG.debug('Loading TrackLengths table...')

    # Get the TrackLengths table as a pandas dataframe
    with db.get_conn(ut.get_database_path(project)) as conn:
        track_lengths = pd.read_sql_query('SELECT track_id, ms_played, '
                                          'frequency, percent_listens '
                                          'FROM TrackLengths;', conn)

    # Add an empty skip column
    track_lengths['skip'] = ''

    # Process each track, identifying skips
    LOG.debug('Identifying skips...')

    grouped = track_lengths.groupby('track_id').apply(
        _determine_skips_for_track)

    # Save to database
    LOG.debug('Saving to database...')

    with db.get_conn(ut.get_database_path(project)) as conn:
        for t, d, s in zip(grouped['track_id'], grouped['ms_played'],
                           grouped['skip']):
            save_skip_datum(t, d, s, conn)


def _determine_skips_for_track(df: pd.DataFrame) -> pd.DataFrame:
    """
    Go through each of the distinct durations for a specific track, marking
    each one as a SKIP or NON_SKIP.

    Args:
        df: A DataFrame containing all the entries from TrackLengths for a
            specific track. This must always contain at least one row,
            and all the rows must have the same track_id.

    Returns:
        The modified DataFrame.
    """

    df['skip'] = [check_frequency(f, p)
                  for f, p in zip(df['frequency'], df['percent_listens'])]

    # If nothing was marked a NON_SKIP, mark the longest duration that's at
    # least the MIN_TRACK_LENGTH as a NON_SKIP, and leave the others to be
    # marked SKIP. It's assumed that the longest duration is the first one.
    if len(df[df['skip'] == SkipState.NON_SKIP]) == 0:
        if df['ms_played'].iloc[0] >= MIN_TRACK_LENGTH:
            df['skip'].iloc[0] = SkipState.NON_SKIP

    # Determine the shortest duration (ms_played) that was marked NON_SKIP
    shortest_non_skip = df[df['skip'] == SkipState.NON_SKIP]['ms_played'].min()

    # Any durations either longer than the shortest_non_skip duration or
    # within a certain percentage of it are marked NON_SKIP as well
    df['skip'] = [check_duration(m, shortest_non_skip, s)
                  for m, s in zip(df['ms_played'], df['skip'])]

    # Lastly, any unset values become SKIP
    df['skip'] = [SkipState.SKIP if s != SkipState.NON_SKIP else s
                  for s in df['skip']]

    return df


def check_frequency(frequency: int,
                    percent_listens: float) -> Optional[SkipState]:
    """
    Determine if a certain duration is a NON_SKIP based on its frequency and
    percent_listens. If the frequency is at least MIN_FREQUENCY and the
    percentage is at least FREQUENCY_PERCENT_THRESHOLD, it's a NON_SKIP.

    If the frequency is at least ABSOLUTE_NON_SKIP_FREQUENCY, it will always
    be set to NON_SKIP, regardless of the percentage.

    Args:
        frequency: The frequency for a certain duration of a certain track.
        percent_listens: This frequency / the total frequency for the track.

    Returns:
        SkipState.NON_SKIP if the condition for NON_SKIP is met. Otherwise,
        just None, to indicate that the state is unknown.
    """

    if frequency >= ABSOLUTE_NON_SKIP_FREQUENCY or \
            (frequency >= MIN_FREQUENCY and
             percent_listens >= FREQUENCY_PERCENT_THRESHOLD):
        return SkipState.NON_SKIP
    else:
        return None


def check_duration(duration: int,
                   shortest_non_skip: Optional[int],
                   current_state: Optional[SkipState]) -> Optional[SkipState]:
    """
    Determine if a certain duration is a NON_SKIP based on its duration
    relative to the other recorded durations of the same track.

    If this duration is longer than any existing NON_SKIP duration, this one
    is also marked NON_SKIP (as it's probably just that song played a little
    and then rewound and played to the end).

    Additionally, if this duration is within SKIP_ERROR_MARGIN percent of any
    other accepted NON_SKIP durations, it is also accepted. That means only
    the very ending of the track was skipped, which is negligible.

    Args:
        duration: This duration length in milliseconds.
        shortest_non_skip: The shortest duration that was already marked
                           NON_SKIP. If no durations are NON_SKIPS yet, this
                           should be None.
        current_state: The current skip state of this duration instance (
                       SKIP, NON_SKIP, or None). If it's already NON_SKIP,
                       NON_SKIP is immediately returned.

    Returns:
        The new skip state for this track duration entry.
    """

    if current_state == SkipState.NON_SKIP:
        return SkipState.NON_SKIP

    if shortest_non_skip and \
            duration >= (1 - SKIP_ERROR_MARGIN) * shortest_non_skip:
        return SkipState.NON_SKIP

    return current_state


def save_skip_datum(track_id: int,
                    ms_played: int,
                    skip: SkipState,
                    conn: sqlite3.Connection) -> None:
    """
    Save skip data for a single row to the TrackLengths table.

    Args:
        track_id: The track id, for identifying the row in the table.
        ms_played: The duration, for identifying the row in the table.
        skip: the SkipState, whose value is stored in the table.
        conn: A connection to the project database.

    Returns:
        None
    """

    conn.execute('UPDATE TrackLengths '
                 'SET skip = ? '
                 'WHERE track_id = ? '
                 'AND ms_played = ?;',
                 (skip.value, track_id, ms_played))
