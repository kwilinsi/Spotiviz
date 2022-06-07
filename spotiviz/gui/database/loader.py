from datetime import datetime
from typing import Dict, Tuple

from spotiviz.projects import utils as ut
from spotiviz.gui.database import sql
from spotiviz.utils import db


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

    with db.get_conn() as conn:
        result = conn.execute(sql.GET_RECENT_PROJECTS, (n,))
        return {p[0]: (p[1], ut.to_datetime(p[2])) for p in result}
