from datetime import date
import os.path
from typing import List, Tuple, Dict

from spotiviz import get_data
from spotiviz.projects import \
    sql, preprocess, checks, utils as ut, spotifyDownload as sd
from spotiviz.utils import db, resources as resc
from spotiviz.utils.log import LOG
from spotiviz.analysis.statistics import stats


def delete_all_projects() -> None:
    """
    Attempt to delete all the current projects. This performs two functions
    for each project:

    1. It removes each of their SQLite database files.
    2. It removes their entries in the global, program-level sqlite database
    that lists all their programs.

    Returns:
        None
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


def create_project(name: str) -> None:
    """
    Create a new project. Add it to the main program database file,
    and create a new database specifically for this project.

    Args:
        name: The name of the project.

    Returns:
        None
    """

    # Check for preexistence of a project with this name
    if checks.does_project_exist(name):
        LOG.error(
            'Attempted to create already-existing project {p}'.format(p=name))
        return

    # Create the project by defining both a database and a SQL entry
    create_project_entry(name)
    create_project_database(name)
    LOG.info('Created a new project: {p}'.format(p=name))


def create_project_entry(name: str) -> None:
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

    Returns:
        None
    """

    with db.get_conn() as conn:
        conn.execute(sql.ADD_PROJECT_ENTRY, (name,))


def create_project_database(name: str) -> None:
    """
    Create a sqlite database file for a project with the given name. Note
    that the name is cleaned by passing through clean_project_name() before
    it is used to create the database.

    IMPORTANT: If there is already a database with this name, it will be
    overwritten.

    Args:
        name: The name of the database.

    Returns:
        None
    """

    db.run_script(resc.get_sql_resource(sql.PROJECT_SETUP_SCRIPT),
                  db.get_conn(ut.clean_project_name(name)))


def preprocess_data(project: str) -> None:
    """
    First, check to make sure that a project with the specified name
    actually exists. If it does call the main preprocessing function.

    Args:
        project: The name of the project.

    Returns:
        None

    Raises:
        ValueError: If the given project name is not recognized.
    """

    # Ensure the project exists first
    checks.enforce_project_exists(project)

    preprocess.main(project)


def add_download(project: str, path: str,
                 name: str = None, download_date: date = None) -> None:
    """
    Create a SpotifyDownload, process it, and save it to the specified
    project all at once.

    Args:
        project: The name of the project.
        path: The path to the directory with the spotify download.
        name: The name to give the download (or omit to default to the name
              of the bottom-level directory in the path).
        download_date: The date that the download was requested from Spotify.

    Returns:
        None
    """

    d = sd.SpotifyDownload(project, path, name, download_date)
    d.save()


def build_project(project: str, root_dir: str,
                  paths: List[Tuple[str, str]]) -> None:
    """
    Create a new project with the specified name. Then bulk add downloads to
    it, saving both the download information and the streaming histories.
    Then clean the streaming histories, merging them into one file.

    Args:
        project: The project.
        root_dir: The root directory in which all the paths can be found.
        paths: A list of tuples for each downloads to add to the project.
               Each tuple should be the path to a download within the root_dir
               and the date the download was requested from Spotify.

    Returns:
        None
    """

    create_project(project)
    for path, d in paths:
        add_download(project, os.path.join(root_dir, path),
                     download_date=ut.to_date(d))

    preprocess_data(project)


def get_stat_summary(project: str) -> Dict:
    """
    Calculate a series of summary statistics for a given project, and return
    it as a dictionary.

    Args:
        project: The project to calculate statistics for.

    Returns:
        None

    Raises:
        ValueError: If the given project name is invalid or the project
                    doesn't exist.
    """

    # Ensure the project exists first
    checks.enforce_project_exists(project)

    # Create the statistics dictionary
    s = dict()

    with db.get_conn(ut.clean_project_name(project)) as conn:
        for name, value in stats.get_stats(conn):
            s[name] = value

    return s
