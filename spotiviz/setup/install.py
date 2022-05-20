import os.path

from spotiviz import get_data
from spotiviz.projects import manager
from spotiviz.utils.log import LOG
from spotiviz.database import db, constants as con


def install_spotiviz():
    """
    Install the Spotiviz application. This primarily entails the creation of
    a database for storing projects.
    """

    LOG.debug('Starting Spotiviz installation')

    # If the data folders don't exist, make them now
    make_dir(get_data(), 'Data')
    make_dir(get_data('sqlite'), 'SQLite')
    make_dir(get_data(os.path.join('sqlite', 'projects')), 'Projects')

    # Delete the program database, if it exists
    if os.path.exists(con.DATABASE_PROGRAM_PATH):
        os.remove(con.DATABASE_PROGRAM_PATH)

    # Initialize database
    db.initialize()

    # Run installation script
    LOG.debug('Running installation script')
    # database.run_script(re.get_sql_resource(sql.SCRIPT_SETUP))

    # Delete any leftover projects
    manager.delete_all_projects()


def make_dir(path: str, name: str) -> None:
    """
    Test whether the given directory exists by its path. If it doesn't exist,
    create it, and log a message to the console indicating that is being
    created.

    Args:
        path: The path to the directory to create.
        name: The name of the directory to use in the log message.

    Returns:
        None
    """

    if not os.path.exists(path):
        LOG.debug('{n} directory not found; creating it now'.format(n=name))
        os.makedirs(path)
