import os.path
import sqlite3

from spotiviz import get_data
from spotiviz.utils.constants import sql


def run_script(script: str, conn: sqlite3.Connection = None) -> None:
    """
    Run the specified script in the specified sqlite connection. If no
    connection is given, the default one to the program's main projects
    database is used.

    Note that the provided connection is automatically closed when after
    executing the script.

    Args:
        script: A path to the .sql script file to execute.
        conn: [Optional] the connection to run, or the main program
        database if none is provided.

    Returns:
        None
    """

    if conn is None:
        conn = get_conn()

    with open(script) as s:
        conn.executescript(s.read())
    conn.close()


def get_conn(file: str = None) -> sqlite3.Connection:
    """
    Initialize a connection to the specified sqlite database file. If no file
    is specified, a connection to the default projects.db file is returned
    that governs the entire spotiviz installation.

    If any file is specified, it is assumed to be a project file,
    and a connection to that file in the data/sqlite/projects directory is
    returned. If that file doesn't already exist, it is created.

    Args:
        file: The name of the database file, ending in .db.

    Returns:
        A connection to the specified database.
    """

    if file is None:
        return sqlite3.connect(
            get_data(os.path.join('sqlite', sql.DATABASE_PROGRAM_NAME)))
    else:
        return sqlite3.connect(
            get_data(os.path.join('sqlite', 'projects', file)))


def get_last_id(conn: sqlite3.Connection) -> int:
    """
    Get the last ID from an auto incrementing column that was generated when
    inserting the most recent record with this connection.

    Args:
        conn: the connection that just inserted some record.

    Returns:
        The autogenerated id that was paired with the inserted record.
    """

    return conn.execute(sql.GET_LAST_ID).fetchone()[0]
