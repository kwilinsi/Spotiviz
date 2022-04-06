import os.path
from spotiviz import get_data
from spotiviz.projects import sql
from spotiviz.projects import utils as ut
from spotiviz.utils import db
from spotiviz.utils import resources as resc
from spotiviz.utils.log import LOG
from spotiviz.projects import spotifyDownload as sd


def delete_all_projects():
    """
    Attempt to delete all the current projects. This performs two functions
    for each project:

    1. It removes each of their sqlite database files
    2. It removes their entries in the global, program-level sqlite database
    that lists all their programs.
    """

    # Delete all the database files
    LOG.debug('Deleting project database files')
    projects_dir = get_data(os.path.join('sqlite', 'projects'))

    for file_name in os.listdir(projects_dir):
        f = os.path.join(projects_dir, file_name)
        if os.path.isfile(f):
            try:
                os.remove(f)
            except OSError:
                LOG.debug('Failed to delete project database: {p}'.format(p=f))

    # Clear the Projects table in the program-level database
    LOG.debug('Clearing Projects table')
    with db.get_conn() as conn:
        conn.execute(sql.CLEAR_ALL_PROJECTS)


def create_project(name: str):
    """
    Create a new project. Add it to the main program database file,
    and create a new database specifically for this project.

    :param name: the name of the project
    """

    # Check for preexistence of a project with this name
    if is_project_exists(name):
        LOG.error(
            'Attempted to create already-existing project {p}'.format(p=name))
        return

    # Create the project by defining both a database and a SQL entry
    create_project_entry(name)
    create_project_database(name)
    LOG.info('Created a new project: {p}'.format(p=name))


def is_project_exists(name: str) -> bool:
    """
    Check whether a project with the given name already exists.

    This is done by ensuring that it has a database file and is present in
    the main program database. If the project exists in one of those
    locations but not the other, it is added to the missing location and True
    is returned.

    Note that the name is case in-sensitive and ignores some characters. See
    clean_project_name() for more information on this behaviour.

    :param name: the name of the project to check
    :return: true if project exists
    """

    # TODO I suspect this doesn't work if one project 'abC d' is created and
    #  then another project 'abcd' is created. The second one will find a
    #  database but no sql entry and it'll try to make a second sql entry for
    #  the same database which is already in use by 'abC d'.

    # Check whether a database with this project name (cleaned) exists
    db_exists = os.path.isfile(
        get_data(os.path.join('sqlite', 'projects',
                              ut.clean_project_name(name)))
    )

    # Check whether there's a project entry with this name (not cleaned) in the
    # Projects table
    with db.get_conn() as conn:
        entry_exists = bool(
            conn.execute(sql.CHECK_PROJECT_EXISTS, (name,)).fetchone())

    # If the entry exists but not the database, make the database
    if entry_exists and not db_exists:
        LOG.debug('Project {p} missing database; making it...'.format(p=name))
        create_project_database(name)

    # If the database exists but not the entry, add the entry
    if db_exists and not entry_exists:
        LOG.debug('Project {p} missing sql entry; adding it...'.format(p=name))
        create_project_entry(name)

    # If either the database or entry previously existed (in which case they
    # both exist now), return true. If neither exist, return false
    return db_exists or entry_exists


def create_project_entry(name: str):
    """
    Create the entry for a project in the main sqlite database for this
    Spotiviz installation.

    If the given project is already in the projects table, nothing happens
    and no data is overwritten.

    Note that the project name doesn't need to be cleaned with
    clean_project_name(). Cleaning is only used while referencing the
    database file, not storing the project name in the SQL database or
    displaying it to the user.

    Args:
        name: The name of the project.
    """

    with db.get_conn() as conn:
        conn.execute(sql.ADD_PROJECT_ENTRY, (name,))


def create_project_database(name: str):
    """
    Create a sqlite database file for a project with the given name. Note
    that the name is cleaned by passing through clean_project_name() before
    it is used to create the database.

    IMPORTANT: If there is already a database with this name, it will be
    overwritten.

    Args:
        name: The name of the database.
    """

    db.run_script(resc.get_sql_resource(sql.PROJECT_SETUP_SCRIPT),
                  db.get_conn(ut.clean_project_name(name)))


def clean_streaming_history(project: str):
    """
    Clean the streaming history in the database of the specified project.
    This entails iterating through the data in the StreamingHistoryRaw table,
    removing duplicates, and transferring it to the StreamingHistory table.

    Args:
        project: The name of the project.

    Raises:
        ValueError: If the given project name is not recognized.
    """

    if not is_project_exists(project):
        raise ValueError('Unrecognized project name {p}'.format(p=project))

    with db.get_conn(ut.clean_project_name(project)) as conn:
        conn.execute(sql.CLEAN_STREAMING_HISTORY)

    LOG.debug('Cleaned streaming history for project {p}'.format(p=project))


def add_download(project: str, path: str, name: str = None):
    """
    Create a SpotifyDownload, process it, and save it to the specified
    project all at once.

    Args:
        project: the name of the project.
        path: the path to the directory with the spotify download.
        name: the name to give the download (or omit to default to the name
        of the bottom-level directory in the path).
    """

    d = sd.SpotifyDownload(project, path, name)
    d.save()
