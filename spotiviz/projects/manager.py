import os.path
from typing import List, Tuple

from sqlalchemy import delete, select

from spotiviz import get_data

from spotiviz.projects import preprocess, checks, utils as ut
from spotiviz.projects.structure import project_class as pc

from spotiviz.database import db
from spotiviz.database.structure.program_struct import Projects

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
        path = os.path.join(projects_dir, file_name)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                LOG.warn(f'Failed to delete project database: \'{path}\'')

    # Clear the Projects table in the program-level database
    LOG.debug('Clearing Projects table')
    with db.session() as session:
        session.execute(delete(Projects))


def create_project(name: str, database_path: str = None) -> pc.Project:
    """
    Create a new project. Add it to the main program database file,
    and create a new database specifically for this project.

    Optionally, you can also specify a database_path where the SQLite
    .database file should be stored. If this is omitted or set to None,
    the database will be placed in the default directory:
    .../spotiviz/data/sqlite/projects/.

    Args:
        name: The name of the project.
        database_path: [Optional] The path to the SQLite database file.

    Returns:
        The newly created project.

    Raises:
        ValueError: If a project with the given name already exists in the
                    program database.
        AssertionError: If there's already an old database file at the
                        selected path, and it can't be removed for some reason
                        (ex. it's currently in use).
    """

    # Check for preexistence of a project with this name
    state = checks.project_state(name)

    # If it already exists, throw an error
    if state == checks.ProjectState.EXISTS:
        raise ValueError(f'Attempted to create already-existing '
                         f'project \'{name}\'')

    # Determine where the project's SQLite database file will be stored
    path = __determine_project_path(project_name=name, path=database_path)

    # Instantiate a new project instance
    project = pc.Project(name, path)

    # If the project already exists, but it's missing a database, simply create
    # a new database file.
    if state == checks.ProjectState.MISSING_DATABASE:
        project.create_database()
        project.update_database()
        LOG.info(f'Project {project} found with missing database. '
                 f'Created new database at \'{path}\'')
        return project

    # If there's already a file at the selected database path, delete that
    # file, as its contents are unknown.
    if os.path.exists(path):
        LOG.debug(f'Deleting unexpected database file at \'{path}\'')
        try:
            os.remove(path)
        except PermissionError:
            raise AssertionError(f'Failed to create a new project {project}. '
                                 f'Couldn\'t remove the old SQLite database '
                                 f'file. The file may be in use by another '
                                 f'process (PermissionError): '
                                 f'\'{path}\'') from None

    # At this point, the project simply doesn't exist yet. Create a SQL entry
    # and a database file for it.
    project.create_database()
    project.save_to_database()

    LOG.info(f'Created a new project: {project}')

    # Load the configuration for the project from the SQLite database
    project.config.read_from_db()

    return project


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
    (though it still converted to an absolute path in case it happens to be
    relative).

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


def preprocess_data(project: pc.Project) -> None:
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
    checks.enforce_project_exists(project.name)

    preprocess.main(project)


def build_project(name: str, root_dir: str,
                  paths: List[Tuple[str, str]],
                  database_path: str = None) -> None:
    """
    This is a convenience method to create a new project with a list of
    Spotify downloads. It performs the following tasks:

    1. Create a new project with the specified name. Add its information to the
    global, program-level database. Create a new SQLite database file for the
    project.

    2. Add the provided Spotify downloads to the project, saving both the
    download information and the streaming histories.

    3. Finally, clean the streaming histories, merging them into one table.

    Args:
        name: The project name.
        root_dir: The root directory in which all the paths can be found.
        paths: A list of tuples for each downloads to add to the project.
               Each tuple should include the path to a download within the
               root_dir and the date the download was requested from Spotify.
               The date should be in the format "%Y-%m-%d". Dates will be
               checked later and possibly adjusted if incorrect.
        database_path: [Optional] A path to the SQLite database file for
                       storing the project data. If this is omitted,
                       the default location is used.

    Returns:
        None
    """

    project = create_project(name, database_path)

    for path, d in paths:
        project.add_download(os.path.join(root_dir, path),
                             download_date=ut.to_date(d))

    preprocess_data(project)


def get_all_projects() -> List[pc.Projects]:
    """
    Get a list of all the projects registered in the Projects table.

    Returns:
        A list of all the projects as SQLAlchemy-based Projects objects.
    """

    with db.session() as session:
        return session.scalars(select(Projects)).all()


def get_project(project_name: str) -> pc.Project:
    """
    Given a project's name, return its Project instance. This assumes that
    the project has already been created and is listed in the global database
    Projects table.

    This also initializes the project's SQLAlchemy database engine and loads
    the project's configuration from the database.

    Args:
        project_name: The name of the project.

    Returns:
        The Project instance for the desired project.

    Raises:
        ValueError: If there is no project with the given name, either
                    because it is not listed in the Projects table or because
                    it's missing a database file. Or because there was some
                    error retrieving the project from the database.
    """

    checks.enforce_project_exists(project_name)

    with db.session() as session:
        try:
            sql_project = session.scalars(
                select(Projects).where(Projects.name == project_name)).one()

            # Create a Project instance from the SQL data
            p = pc.Project.from_sql(sql_project)

            # Initialize SQLAlchemy engine and load config
            p.initialize_engine()
            p.config.read_from_db()

            return p
        except Exception:
            raise ValueError(f'Failed to get project \'{project_name}\'')
