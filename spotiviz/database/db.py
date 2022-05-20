from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from spotiviz.database import constants as con

GLOBAL_ENGINE = None

Session = scoped_session(sessionmaker())


def initialize() -> None:
    """
    Initialize the engine for the global project-level database Session.
    Returns:
        None
    """

    global GLOBAL_ENGINE, Session

    GLOBAL_ENGINE = create_engine(f'sqlite:///{con.DATABASE_PROGRAM_PATH}',
                                  echo=True, future=True)
    Session.configure(bind=GLOBAL_ENGINE)
