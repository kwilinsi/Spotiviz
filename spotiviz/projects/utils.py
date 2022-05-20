import datetime
import re
from datetime import date, timedelta, datetime
from typing import Optional, Iterable

from spotiviz.utils import db
from spotiviz.projects import sql

# NOTE: This file intentionally does not have any dependencies within the
# spotiviz.projects package (except the sql file). Therefore, it can be
# freely imported by those files without risk of circular dependencies.


# This format is used for storing dates in the SQLite database
__DATE_FORMAT = '%Y-%m-%d'

# This format is used for storing complete timestamps
__DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def clean_project_name(name: str) -> str:
    """
    This cleans a project name. It is converted to lowercase, and all
    characters except letters, numbers, hyphens, and underscores are removed.

    This is primarily used for setting the names of database files for each
    project. The project name is not cleaned in the main program database for
    the entire Spotiviz installation.

    This also adds .database to the file name if it was not there initially. Note
    that this is the only . that is allowed in the returned string.

    Args:
        name: The name to clean.

    Returns:
        The cleaned name.
    """

    n = name.lower()
    return re.sub(r'[^\w-]', '', n[:-3] if n.endswith('.database') else n) + '.database'


def get_database_path(project: str) -> str:
    """
    Given the name of a project, return the path to its SQLite database file.
    This is found by querying the Projects table in the main program.database
    database.

    Args:
        project: The name of the project.

    Returns:
        The path to the project's SQLite database file.

    Raises:
        ValueError: If the given project does not exist.
    """

    with db.get_conn() as conn:
        try:
            return conn.execute(sql.GET_PROJECT_PATH, (project,)).fetchone()[0]
        except Exception:
            raise ValueError("There is no project '{p}'".format(p=project))


def date_range(start_date: date, end_date: date) -> Iterable[date]:
    """
    Yields individual dates through an iterator in a range from the start to
    ending dates, similar to the range() function.

    Args:
        start_date: The first date (inclusive).
        end_date: The last date (exclusive).

    Returns:
        The next date in the sequence.

    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def to_date(date_str: str) -> Optional[datetime]:
    """
    Convert the given date string to a proper datetime.date instance using the
    format "%Y-%m-%d".

    Args:
        date_str: The date as a string.

    Returns:
        The date as a date object, or None if the given string is None.

    Raises:
        ValueError: If the provided date string fails while parsing to a date
                    object.
    """

    if date_str is None:
        return None

    try:
        return datetime.strptime(date_str, __DATE_FORMAT)
    except Exception:
        raise ValueError("Invalid date_str '" + date_str +
                         "' cannot be parsed to a date object.")


def to_datetime(time_str: str) -> Optional[datetime]:
    """
    Analogous to utils.to_date() but operating on full timestamps rather than
    simply dates, this function accepts a timestamp as a string and returns
    it as a proper datetime object.

    Args:
        time_str: The string to convert to a datetime object.

    Returns:
        The datetime object, or None if the given string is None.

    Raises:
        ValueError: If the provided time string fails while parsing to a
                    datetime object.
    """

    if time_str is None:
        return None

    try:
        return datetime.strptime(time_str, __DATETIME_FORMAT)
    except Exception:
        raise ValueError("Invalid time_str '" + time_str +
                         "' cannot be parsed to a datetime object.")


def date_to_str(date_obj: date) -> str:
    """
    This is the opposite of the to_date() function. It accepts as a parameter
    some datetime.date object and returns it as a string in the format
    "%Y-%m-%d".

    Args:
        date_obj: The date object.

    Returns:
        The date as a formatted string, or an empty string if the given date
        is null.

    Raises:
        ValueError: If there is some error while attempting to format the date.
    """

    if date_obj is None:
        return ''

    try:
        return date_obj.strftime(__DATE_FORMAT)
    except Exception:
        raise ValueError("Invalid date object '" + str(date_obj) +
                         "' cannot be formatted as a date string.")
