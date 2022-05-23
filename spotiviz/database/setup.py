"""
This script sets up the SQLite database structures using the appropriate
engine and structure file.
"""

import sqlalchemy as sa
from sqlalchemy import text

from spotiviz.database import db, sql
from spotiviz.database.structure import program_struct, project_struct

from spotiviz.utils import resources


def setup_program_db() -> None:
    """
    Set up the SQLite database structure for the global program-level
    database. This assumes that the database has been initialized. See
    database.db.initialize().

    Returns:
        None
    """

    program_struct.Base.metadata.create_all(db.GLOBAL_ENGINE)


def setup_project_db(project_engine: sa.engine.base.Engine) -> None:
    """
    Set up the SQLite database structure for an individual project database
    file.

    Args:
        project_engine: The engine connected to the project database file.

    Returns:
        None
    """

    # Set up the main tables
    project_struct.Base.metadata.create_all(project_engine)

    # Set up the StreamingHistoryFull view
    with project_engine.connect() as conn:
        with open(resources.get_sql_resource(
                sql.VIEW_STREAMING_HISTORY_FULL)) as file:
            conn.execute(text(file.read()))
