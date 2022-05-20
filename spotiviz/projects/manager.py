import datetime
from datetime import date
import os.path
from typing import List, Tuple, Dict

from spotiviz import get_data
from spotiviz.projects import (
    sql, preprocess, checks, utils as ut, spotifyDownload as sd)
from spotiviz.utils import db, resources as resc
from spotiviz.utils.log import LOG


def delete_all_projects() -> None:
    """
    Attempt to delete all the current projects. This performs two functions
    for each project:

    1. It removes each of their SQLite database files.
    2. It removes their entries in the global, program-level sqlite database
    that lists all their programs.

    Note that this only deletes project databases stored in the standard
    location. If a database was stored at a custom path outside the
    spotiviz/data/projects directory, it will not be deleted.

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


def create_project(name: str, database_path: str = None) -> None:
    """
    Create a new project. Add it to the main program database file,
    and create a new database specifically for this project.

    Optionally, you can also specify a database_path where the SQLite .database file
    should be stored. If this is omitted or set to None, the database will be
    placed in the default directory: ~/spotiviz/data/sqlite/projects/.

    Args:
        name: The name of the project.
        database_path: [Optional] The path to the SQLite database file.

    Returns:
        None
    """

    # Check for preexistence of a project with this name
    state = checks.project_state(name)
    if state == checks.ProjectState.EXISTS:
        LOG.error("Attempted to create already-existing "
                  "project '{p}'".format(p=name))
        return

    # Determine where the project's SQLite database file will be stored
    path = __determine_project_path(project_name=name, path=database_path)

    # If the project already exists, but it's missing a database, simply create
    # a new database file.
    if state == checks.ProjectState.MISSING_DATABASE:
        create_project_database(path)
        update_project_database_path(name, path)
        LOG.info("Project '{p}' found with missing database. "
                 "Created new database at '{d}'".format(p=name, d=path))
        return

    # At this point, the project simply doesn't exist yet. Create a SQL entry
    # and a database file for it.
    create_project_entry(name, path)
    create_project_database(path)
    LOG.info("Created a new project: '{p}'".format(p=name))


def __determine_project_path(project_name: str, path: str = None) -> str:
    """
    Determine where a new project's database is to be stored based on the
    given project name and path.

    If only the project_name is given and not the path, then the project's
    database will be stored in the default location:
    ~/spotiviz/sqlite/data/projects/. The project name will be cleaned and
    appended to that directory.

    However, if a path is explicitly provided by the user, that will override
    the default location. If the given path points to a valid, existing
    directory, then the database will be stored in there (according to the
    name of the project).

    If the path doesn't point to a valid directory, it's assumed that it
    points to a file instead (regardless of whether that file exists). In this
    case, the project_name is ignored and the path is simply returned as-is
    (though it still converted to an abspath in case it happens to be relative).

    --

    Note: At no time is any check performed to see if there's already a file
    at the final database path. If a file is there already, it will be
    overwritten.

    Args:
        project_name: The name of the project.
        path: [Optional] A path to an explicit location for the database.

    Returns:
        The project's database path.
    """

    if path is None:
        return get_data(os.path.join(
            'sqlite', 'projects', ut.clean_project_name(project_name)))
    elif os.path.isdir(path):
        return os.path.abspath(
            os.path.join(path, ut.clean_project_name(project_name)))
    else:
        return os.path.abspath(path)


def create_project_entry(name: str, database_path: str) -> None:
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
        database_path: The path to the SQLite database file.

    Returns:
        None
    """

    with db.get_conn() as conn:
        conn.execute(sql.ADD_PROJECT_ENTRY, (name, database_path))


def create_project_database(path: str) -> None:
    """
    Create a SQLite database file at the specified path. Perform the
    initial setup of the SQL environment to make it a project.

    IMPORTANT: If there is already a file at this path, it will be overwritten.

    Args:
        path: The path to the SQLite database file.

    Returns:
        None
    """

    db.run_script(resc.get_sql_resource(sql.PROJECT_SETUP_SCRIPT),
                  db.get_conn(path))


def update_project_database_path(project: str, path: str) -> None:
    """
    Update a project to use a new database file.

    Args:
        project: The name of the project.
        path: The path to the new database file.

    Returns:
        None
    """

    with db.get_conn() as conn:
        conn.execute(sql.UPDATE_PROJECT_PATH, (project, path))


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
                  paths: List[Tuple[str, str]],
                  database_path: str = None) -> None:
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
        database_path: [Optional] A path to the SQLite database file for
                       storing the project data.

    Returns:
        None
    """

    create_project(project, database_path)
    for path, d in paths:
        add_download(project, os.path.join(root_dir, path),
                     download_date=ut.to_date(d))

    preprocess_data(project)


def get_all_projects() -> Dict[str, Tuple[str, datetime.datetime]]:
    """
    Get a list of all the projects registered in the Projects table.

    This is given as a Python dictionary. Each project name is a key, and the
    values are tuples of the database path and the creation timestamp.

    Returns:
        A dictionary with each project name listed as a key.
    """

    with db.get_conn() as conn:
        result = conn.execute(sql.GET_ALL_PROJECTS)
        return {p[0]: (p[1], ut.to_datetime(p[2])) for p in result}
