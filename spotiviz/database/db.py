from typing import Dict, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session

from spotiviz.database import constants as con

GLOBAL_ENGINE = None

PROJECT_ENGINES: Dict[str, sa.engine.Engine] = {}


def _create_engine(path: str) -> sa.engine.Engine:
    """
    Create an SQLAlchemy engine for a SQLite database using the standard
    configuration.

    Args:
        path: The path to the SQLite database file.

    Returns:
        The engine.
    """

    return sa.create_engine(f'sqlite:///{path}', echo=True, future=True)


def initialize() -> None:
    """
    Initialize the engine for the global project-level database Session.
    Returns:
        None
    """

    global GLOBAL_ENGINE

    GLOBAL_ENGINE = _create_engine(con.DATABASE_PROGRAM_PATH)


def initialize_project_engine(name: str, path: str) -> sa.engine.Engine:
    """
    Create a new SQLAlchemy engine for a project and save it to the
    db.PROJECT_ENGINES dictionary.

    Args:
        name: The project name, which will be used as a key for future
              retrieval of this project engine in the PROJECT_ENGINES
              dictionary.
        path: The path to the project's SQLite database, used for
              establishing the engine.

    Returns:
        The newly created engine.
    """

    global PROJECT_ENGINES

    e = _create_engine(path)
    PROJECT_ENGINES[name] = e
    return e


def get_project_engine(name: str,
                       path: Optional[str] = None) -> sa.engine.Engine:
    """
    Retrieve an SQLAlchemy engine for a particular project, if such an engine
    exists. The PROJECT_ENGINES dictionary is checked for a key matching the
    provided project name.

    If the engine doesn't exist, it is created at the specified path. If no
    path is given, an exception is raised.

    Args:
        name: The name of the project.
        path: Optionally, the path to the project's database (in case the
              engine doesn't exist).

    Returns:
        The requested engine.

    Raises:
        ValueError: If the provided name does not correspond to an existing
                    engine and no path is given to create a new engine.
    """

    try:
        return PROJECT_ENGINES[name]
    except:
        if path:
            return initialize_project_engine(name, path)
        raise ValueError(f'There is no engine matching the project name '
                         f'"{name}".')


def session(project_name: str = None) -> Session:
    """
    Return a new Session instance created from an SQLAlchemy engine. If a
    project name is specified, that project's engine is retrieved from the
    PROJECT_ENGINES dictionary. If no project name is given, then the
    GLOBAL_ENGINE is used and a session to the global program-level database
    is returned.

    Note to use the GLOBAL_ENGINE, it must be initialized with db.initialize()
    first. To use a project engine, it must be initialized with
    db.initialize_project_engine().

    If a project_name is given that does not have a matching engine,
    an exception will be raised.

    Returns:
        A new session instance.

    Raises:
        ValueError: If a project_name is given that doesn't have a matching
                    engine in the PROJECT_ENGINES dictionary.
        AttributeError: If the GLOBAL_ENGINE is used by it has not been
                        initialized with db.initialize() yet.

    """

    if project_name:
        return Session(get_project_engine(project_name), autoflush=True)
    else:
        if GLOBAL_ENGINE:
            return Session(GLOBAL_ENGINE, autoflush=True)
        else:
            raise AttributeError('Global engine requested without '
                                 'initialization.')
