from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spotiviz.database import constants as con

GLOBAL_ENGINE = None


def initialize() -> None:
    """
    Initialize the engine for the global project-level database Session.
    Returns:
        None
    """

    global GLOBAL_ENGINE

    GLOBAL_ENGINE = create_engine(f'sqlite:///{con.DATABASE_PROGRAM_PATH}',
                                  echo=True, future=True)


def program_session() -> Session:
    """
    Return a new Session instance created from the GLOBAL_ENGINE. Note that
    the engine must be initialized with db.initialize() first.

    Returns:
        A new session instance.

    """

    return Session(GLOBAL_ENGINE)
