import os.path

from spotiviz.utils import resources as re
from spotiviz.utils import db
from spotiviz.utils.constants import sql
from spotiviz.utils.log import LOG
from spotiviz.projects import manager
from spotiviz import get_data


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

    # Run installation script
    LOG.debug('Running installation script')
    db.run_script(re.get_sql_resource(sql.SCRIPT_SETUP))

    # Delete any leftover projects
    manager.delete_all_projects()


def make_dir(path: str, name: str):
    """
    Test whether the given directory exists by its path. If it doesn't exist,
    create it, and log a message to the console indicating that is being
    created.

    Args:
        path: the path to the directory to create
        name: the name of the directory to use in the log message
    """

    if not os.path.exists(path):
        LOG.debug('{n} directory not found; creating it now'.format(n=name))
        os.makedirs(path)
