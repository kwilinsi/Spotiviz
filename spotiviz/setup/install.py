import os.path

from spotiviz import get_data
from spotiviz.utils.log import LOG

from spotiviz.database import db, setup, constants as con
from spotiviz.database.structure.program_struct import Config as ConfigTbl

from spotiviz.projects import manager
from spotiviz.projects.structure.config.properties import Config


def install_spotiviz():
    """
    Install the Spotiviz application. This primarily entails the creation of
    a database for storing projects.

    If there is already a program database file, it is deleted, and a new one
    is created.
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
    setup.setup_program_db()

    # Delete old project files
    manager.delete_all_projects()

    # Load the default project configuration
    load_default_config()


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


def load_default_config() -> None:
    """
    Populate the Config table in the program SQLite database. The default
    properties for projects are set according to their defaults within the
    _Property class.

    Returns:
        None
    """

    # Create SQLAlchemy Config objects

    # noinspection PyArgumentList
    configs = [ConfigTbl(key=prop.name,
                         value=prop.value.default,
                         is_project_default=True)
               for prop in Config]

    # Add each object to the Config table
    with db.session() as session:
        session.add_all(configs)
        session.commit()
