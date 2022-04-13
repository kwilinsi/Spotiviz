from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List

from spotiviz.utils import db, resources as resc
from spotiviz.utils.log import LOG
from spotiviz.projects import sql, utils as ut

# This format is used for storing dates in the SQLite database
DATE_FORMAT = '%Y-%m-%d'


def main(project: str):
    """
    After the data from a Spotify download has been stored in the project,
    it needs to undergo some initial preprocessing. This allows the data to
    be more easily analyzed later.

    The following preprocessing steps are performed on the given project:

    1. Clean the streaming history in the database of the specified project.
       This entails iterating through the data in the StreamingHistoryRaw table,
       removing duplicates, and transferring it to the StreamingHistory table.

    2. Assemble a list of all the dates in the given download range, storing
       them in the ListenDates table. Label the dates according to whether
       they have listening data in the StreamingHistory table.

    3. Identify dates that are missing, meaning they are not captured within
       the listening history range for any of the downloads in the project,
       and label them accordingly.

    4. Look for any date anomalies, where a date was marked as has_listen =
       TRUE and is_missing = TRUE. Obviously, it can't be both missing and
       have a listen recorded, so is_missing is set to FALSE in these cases.

    Precondition:
        The given project name MUST be valid, as it is not checked.

    Args:
        project: The name of the project (MUST be valid--not checked).
    """

    LOG.debug('Started preprocessing for project {p}'.format(p=project))

    # Clean the streaming history
    LOG.debug('  Cleaning streaming history...')
    db.run_script(resc.get_sql_resource(sql.CLEAN_STREAMING_HISTORY_SCRIPT),
                  db.get_conn(ut.clean_project_name(project)))

    # Set the list of dates
    LOG.debug('  Listing dates...')
    list_dates(project)

    # Find missing dates
    LOG.debug('  Identifying missing dates...')
    identify_missing_dates(project)

    # Correct date anomalies
    LOG.debug('  Correcting date anomalies...')
    db.run_script(resc.get_sql_resource(sql.CLEAN_STREAMING_HISTORY_SCRIPT),
                  db.get_conn(ut.clean_project_name(project)))


def list_dates(project: str):
    """
    This populates the ListenDates table with a list of every day between the
    first and last date found in the StreamingHistoryRaw table.

    Args:
        project: The name of the project. (Must be valid; not checked).
    """

    with db.get_conn(ut.clean_project_name(project)) as conn:
        # Get a list of all the dates for which there is listening history
        query = conn.execute(sql.GET_ALL_INCLUDED_DATES)
        dates_incl = [ut.to_date(f[0]) for f in query]

        # Get the first and last date with listening history
        first_date = dates_incl[0]
        last_date = dates_incl[-1]

        # Add every date from first to last date to the Dates table
        for d in ut.date_range(first_date,
                               last_date + timedelta(days=1)):
            conn.execute(sql.ADD_DATE, (ut.date_to_str(d),
                                        d in dates_incl))


def identify_missing_dates(project: str):
    """
    This updates the Dates table to indicate whether each date is marked
    missing, meaning it is not captured by any of the Downloads.

    Args:
        project: The name of the project. (Must be valid; not checked).
    """

    with db.get_conn(ut.clean_project_name(project)) as conn:
        # Get a list of download dates for all the downloads
        query = conn.execute(sql.GET_DOWNLOAD_DATES)
        download_dates = [ut.to_date(f[0]) for f in query]

        query = conn.execute(sql.GET_ALL_DATES)
        all_dates = [ut.to_date(f[0]) for f in query]

        # Check each date to see if it's missing
        for d in all_dates:
            conn.execute(sql.UPDATE_DATE_MISSING_STATUS,
                         (is_date_missing(d, download_dates),
                          ut.date_to_str(d)))


def is_date_missing(this_date: date, download_dates: List[date]) -> bool:
    """
    Determine if the given date is contained within the timespan of a set of
    download dates.

    Args:
        this_date: The date to check.
        download_dates: The list of download end dates.

    Returns: True if the given date is contained in the date range for one of
             the download dates; otherwise False.
    """

    for end_date in download_dates:
        start_date = end_date - relativedelta(years=1)
        if start_date <= this_date <= end_date:
            return False
    return True
