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
from typing import Optional, List
import pandas as pd
from sqlalchemy import select
from itertools import groupby

from spotiviz.utils.log import LOG
from spotiviz.projects import utils as ut
from spotiviz.projects.structure import project_class as pc

from spotiviz.database.structure.project_struct import TrackLengths

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

    SKIP = 1
    NON_SKIP = 2


def determine_skips(project: pc.Project) -> None:
    """
    For each track recorded in a project, go through each of the durations that
    it was played for by iterating over the TrackLengths table. Determine
    which of those durations should be marked a SKIP.

    Args:
        project: The project to process.

    Returns:
        None
    """

    LOG.debug('Loading TrackLengths table...')

    # Get the TrackLengths table as a pandas DataFrame
    with project.open_session() as session:
        track_durations = session.scalars(
            select(TrackLengths).order_by(TrackLengths.track_id)).all()

        # Group by tracks
        tracks = [list(t[1])
                  for t in groupby(track_durations, lambda x: x.track_id)]

        LOG.debug('Identifying skips...')

        # Each track group is a collection of durations
        for track in tracks:
            _determine_skips_for_track(track)

        # Save to database
        LOG.debug('Saving to database...')

        session.commit()


def _determine_skips_for_track(
        durations: List[TrackLengths]) -> List[TrackLengths]:
    """
    Go through each of the distinct durations for a specific track, marking
    each one as a SKIP or NON_SKIP.

    Args:
        durations: A list of TrackLengths objects, one for each of the
                   durations that a certain track was played for. This must
                   always contain at least one element, and all elements must
                   have the same track_id.

    Returns:
        The modified list, with the skip data members modified for each
        TrackLengths object.
    """

    any_non_skips = False

    for d in durations:
        d.skip = check_frequency(d.frequency, d.percent_listens)
        if d.skip:
            any_non_skips = True

    # If nothing was marked a NON_SKIP, mark the longest duration that's at
    # least the MIN_TRACK_LENGTH as a NON_SKIP, and leave the others to be
    # marked SKIP. It's assumed that the longest duration is the first one.
    if not any_non_skips:
        if durations[0].ms_played >= MIN_TRACK_LENGTH:
            durations[0].skip = SkipState.NON_SKIP

    # Determine the shortest duration (ms_played) that was marked NON_SKIP
    non_skips = [d.ms_played
                 for d in durations if d.skip == SkipState.NON_SKIP]
    shortest_non_skip = min(non_skips) if non_skips else None

    # Any durations either longer than the shortest_non_skip duration or
    # within a certain percentage of it are marked NON_SKIP as well
    for d in durations:
        d.skip = check_duration(d.ms_played, shortest_non_skip, d.skip)

    # Lastly, any unset values become SKIP
    for d in durations:
        if d.skip != SkipState.NON_SKIP:
            d.skip = SkipState.SKIP

    # Clean up by converting SkipStates to integers
    for d in durations:
        d.skip = d.skip.value

    return durations


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
                    conn) -> None:
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
