"""
This script sets up the SQLite database structures using the appropriate
engine and structure file.
"""

import sqlalchemy as sa
from sqlalchemy import text, select

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

    # Load the default project configuration from the program database
    with db.session() as session:
        stmt = select(program_struct.Config).where(
            program_struct.Config.is_project_default == True)
        result = session.scalars(stmt)

        # Map the default project configuration to Config objects
        # noinspection PyArgumentList
        configs = [project_struct.Config(key=r.key,
                                         value=r.value)
                   for r in result]

    # Set up the StreamingHistoryFull view and save default configuration
    with db.session(engine=project_engine) as session:
        session.add_all(configs)

        with open(resources.get_sql_resource(
                sql.VIEW_STREAMING_HISTORY_FULL)) as file:
            session.execute(text(file.read()))

        session.commit()
