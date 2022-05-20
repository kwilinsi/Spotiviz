"""
This script is used to run some basic initialization for the Spotiviz program.
It primarily configures and starts the database connection, allowing other
modules to access tables and configuration settings.
"""

import os.path

from sqlalchemy import create_engine
from spotiviz import db, get_data
from spotiviz.utils.constants import sql


def init_db() -> None:
    """
    Configure the main project-level database session.
    Returns:
        None
    """

    db.GLOBAL_ENGINE = create_engine('sqlite:///{path}'.format(
        path=get_data(os.path.join('sqlite', sql.DATABASE_PROGRAM_NAME))
    ), echo=True)

    db.Session.configure(bind=db.GLOBAL_ENGINE)
