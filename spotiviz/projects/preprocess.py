from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List

from sqlalchemy import func, select, text
from sqlalchemy.dialects.sqlite import DATE
from sqlalchemy.orm import Session

from spotiviz.utils import resources as resc
from spotiviz.utils.log import LOG
from spotiviz.projects import sql, utils as ut
from spotiviz.projects.structure import project_class as pc

from spotiviz.database.structure.project_struct import (
    Downloads, ListenDates, StreamingHistory
)


def main(project: pc.Project) -> None:
    """
    After the data from a Spotify download has been stored in the project,
    it needs to undergo some initial preprocessing. This allows the data to
    be more easily analyzed later.

    The following preprocessing steps are performed on the given project:

    1. Populate the Artists and Tracks tables with all the unique artist and
       track names.

    2. Clean the streaming history in the database of the specified project.
       This entails iterating through the data in the StreamingHistoryRaw table,
       removing duplicates, and transferring it to the StreamingHistory table.

    3. Populate the TrackLengths table with frequencies for each track and
       ms_played pair.

    4. Assemble a list of all the dates in the given download range, storing
       them in the ListenDates table. Label the dates according to whether
       they have listening data in the StreamingHistory table.

    5. Identify dates that are missing, meaning they are not captured within
       the listening history range for any of the downloads in the project,
       and label them accordingly.

    6. Look for any date anomalies, where a date was marked as has_listen =
       TRUE and is_missing = TRUE. Obviously, it can't be both missing and
       have a listen recorded, so is_missing is set to FALSE in these cases.

    Precondition:
        The given project name MUST be valid, as it is not checked.

    Args:
        project: The name of the project (MUST be valid--not checked).

    Returns:
        None
    """

    LOG.debug(f'Started preprocessing for project {project}')

    with project.open_session() as session:
        # Populate Artists and Tracks tables
        LOG.debug('  Loading artists and tracks...')
        with open(resc.get_sql_resource(sql.LOAD_ARTISTS_SCRIPT)) as f:
            session.execute(text(f.read()))
        with open(resc.get_sql_resource(sql.LOAD_TRACKS_SCRIPT)) as f:
            session.execute(text(f.read()))

        # Clean the streaming history
        LOG.debug('  Cleaning streaming history...')
        with open(resc.get_sql_resource(
                sql.CLEAN_STREAMING_HISTORY_SCRIPT)) as f:
            session.execute(text(f.read()))

        # Populate TrackLengths table
        LOG.debug('  Computing TrackLengths frequencies...')
        with open(resc.get_sql_resource(sql.LOAD_TRACK_LENGTHS_SCRIPT)) as f:
            session.execute(text(f.read()))

        # Set the list of dates
        LOG.debug('  Classifying dates...')
        populate_listen_dates(session)

        # Correct date anomalies
        LOG.debug('  Correcting date anomalies...')
        with open(resc.get_sql_resource(
                sql.CORRECT_DATE_ANOMALIES_SCRIPT)) as f:
            session.execute(text(f.read()))


def populate_listen_dates(session: Session) -> None:
    """
    This populates the ListenDates table with a list of every day between the
    first and last date found in the StreamingHistoryRaw table.

    Args:
        session: An SQLAlchemy session for the project.

    Returns:
        None
    """

    # Get a list of all the dates for which there is listening history
    sh_date = func.date(StreamingHistory.end_time, type_=DATE)
    result = session.scalars(select(sh_date)
                             .group_by(sh_date)
                             .order_by(sh_date))
    included_dates = result.all()

    # Get a list of download dates for all the downloads
    result = session.scalars(select(Downloads.download_date))
    download_dates = result.all()

    print(f'Result: type {type(result)}, contents {result}')
    print(f'dates_incl: type {type(included_dates)}, '
          f'type element 1 {type(included_dates[0])}, '
          f'contents {included_dates[:10]}')

    # Get the first and last date with recorded listening history
    first_date = included_dates[0]
    last_date = included_dates[-1]

    # Get a list of ListenDates objects for every date in the range [first,
    # last] and their has_listen and is_missing states

    # noinspection PyArgumentList
    dates = [ListenDates(day=d,
                         has_listen=d in included_dates,
                         is_missing=d not in included_dates and
                                    is_date_missing(d, download_dates))
             for d in ut.date_range(first_date, last_date + timedelta(days=1))]

    # Add all the dates to the database
    session.add_all(dates)


def is_date_missing(this_date: date, download_dates: List[date]) -> bool:
    """
    Determine if the given date is contained within the timespan of a set of
    download dates.

    Args:
        this_date: The date to check.
        download_dates: The list of download end dates.

    Returns: True if and only if the given date is NOT contained in the date
             range for ANY of the download dates.
    """

    for end_date in download_dates:
        start_date = end_date - relativedelta(years=1)
        if start_date <= this_date <= end_date:
            return False
    return True
