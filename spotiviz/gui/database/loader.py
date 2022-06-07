from datetime import datetime
from typing import Dict, Tuple

from sqlalchemy import select

from spotiviz.database import db
from spotiviz.database.structure.program_struct import Projects


def get_recent_projects(n: int = -1) -> Dict[str, Tuple[str, datetime]]:
    """
    Get a list of recently accessed projects registered in the Projects table.

    This is given as a Python dictionary. Each project name is a key, and the
    values are tuples of the database path and the creation timestamp.

    Args:
        n: The number of projects to retrieve. If omitted, it defaults to -1,
           which lists every project with no limit.


    Returns:
        A dictionary with each project name listed as a key.
    """

    with db.session() as session:
        stmt = select(Projects).order_by(Projects.created_at.desc())
        if n > 0:
            stmt = stmt.limit(n)

        result = session.execute(stmt)

        return {r[0].name: (r[0].database_path, r[0].created_at)
                for r in result}
