from spotiviz.utils import db
from spotiviz.utils import resources as resc
from spotiviz.projects import sql
from spotiviz.projects import utils as ut
from spotiviz.utils.log import LOG


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
    Add a list of all the dates in the time range encapsulated by the
    downloads in this project to the Dates table. Indicate whether each date
    has some listening history and whether its missing altogether.

    Args:
        project: the name of the project (MUST be valid)
    """

    with db.get_conn(ut.clean_project_name(project)) as conn:
        min_date = conn.execute(sql.CALCULATE_MIN_DATE).fetchone()[0]
        max_date = conn.execute(sql.CALCULATE_MAX_DATE).fetchone()[0]
        print('min_date =', min_date)
        print('max_date =', max_date)

        for date in ut.date_range(min_date, max_date):
            conn.execute(sql.ADD_DATE, (date,))
