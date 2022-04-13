import datetime

from spotiviz.utils import db
from spotiviz.utils import resources as resc
from spotiviz.projects import sql
from spotiviz.projects import utils as ut
from spotiviz.utils.log import LOG

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

    2. Assemble a list of all the dates in the given download range. Label
       the dates according to whether they have listening data and whether
       they're missing (not captured within the listening history range for
       any of the downloads in the project).

    Precondition:
        The given project name MUST be valid, as it is not checked.

    Args:
        project: the name of the project (MUST be valid--not checked)
    """

    LOG.debug('Started preprocessing for project {p}'.format(p=project))

    # Clean the streaming history
    clean_streaming_history(project)

    # Set the list of dates
    get_dates(project)


def clean_streaming_history(project: str):
    """
    Run the script that cleans the streaming history, copying it from the
    StreamingHistoryRaw table to the StreamingHistory table and removing
    duplicate entries.

    Args:
        project: the name of the project (MUST be valid)
    """

    db.run_script(resc.get_sql_resource(sql.CLEAN_STREAMING_HISTORY_SCRIPT),
                  db.get_conn(ut.clean_project_name(project)))


def get_dates(project: str):
    """
    This populates the Dates table with a list of every day between the first
    and last date found in the StreamingHistoryRaw table.

    Args:
        project: The name of the project. (Must be valid; not checked).
    """

    with db.get_conn(ut.clean_project_name(project)) as conn:
        # Get a list of all the dates for which there is listening history
        dates_incl = [
            datetime.datetime.strptime(f[0], DATE_FORMAT)
            for f in conn.execute(sql.GET_ALL_INCLUDED_DATES)
        ]

        # Get the first and last date with listening history
        first_date = dates_incl[0]
        last_date = dates_incl[-1]

        # Add every date from first to last date to the Dates table
        for d in ut.date_range(first_date,
                               last_date + datetime.timedelta(days=1)):
            conn.execute(sql.ADD_DATE, (d.strftime(DATE_FORMAT),
                                        d in dates_incl))
