import datetime
import os.path
import re
from datetime import date, timedelta, datetime
from typing import Optional, Iterable
from sqlalchemy import select

from spotiviz import get_data

from spotiviz.database import db
from spotiviz.database.structure.program_struct import Projects

# NOTE: This file intentionally does not have any dependencies within the
# spotiviz.projects package (except the sql file). Therefore, it can be
# freely imported by those files without risk of circular dependencies.


# This format is used for storing dates in the SQLite database
__DATE_FORMAT = '%Y-%m-%d'


def clean_project_name(name: str) -> str:
    """
    This cleans a project name. It is converted to lowercase, and all
    characters except letters, numbers, hyphens, and underscores are removed.

    This is primarily used for setting the names of database files for each
    project. The project name is not cleaned in the main program database for
    the entire Spotiviz installation.

    This also adds .database to the file name if it was not there initially.
    Note
    that this is the only . that is allowed in the returned string.

    Args:
        name: The name to clean.

    Returns:
        The cleaned name.
    """

    n = name.lower()
    return re.sub(r'[^\w-]', '',
                  n[:-3] if n.endswith('.db') else n) + '.db'


def get_database_path(project: str) -> str:
    """
    Given the name of a project, return the path to its SQLite database file.
    This is found by querying the Projects table in the main program.db
    database.

    Args:
        project: The name of the project.

    Returns:
        The path to the project's SQLite database file.

    Raises:
        ValueError: If the given project does not exist.
    """

    with db.session() as session:
        try:
            r = session.scalars(
                select(Projects.database_path).where(Projects.name == project))
            return r.one()
        except Exception:
            raise ValueError("There is no project '{p}'".format(p=project))


def date_range(start_date: date, end_date: date) -> Iterable[date]:
    """
    Yields individual dates through an iterator in a range from the start to
    ending dates, similar to the range() function.

    Args:
        start_date: The first date (inclusive).
        end_date: The last date (exclusive).

    Yields:
        The next date in the sequence.

    Returns:
        An interator of dates.

    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def to_date(date_str: str) -> Optional[date]:
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
        return datetime.strptime(date_str, __DATE_FORMAT).date()
    except Exception:
        raise ValueError(f'Invalid date_str "{date_str}" cannot be parsed '
                         f'to a date object.')


def to_datetime(time_str: str) -> Optional[datetime]:
    """
    Analogous to utils.to_date() but operating on full timestamps rather than
    simply dates, this function accepts a timestamp as a string and returns
    it as a proper datetime object.

    This works for timestamps with and without seconds. The format without
    seconds is used first, and if that failed, it is repeated with a seconds
    parameter. If both attempts fail, a ValueError is raised.

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
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        try:
            return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            raise ValueError(f'Invalid time_str {time_str} '
                             f' cannot be coerced into a datetime object.')


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
        raise ValueError(f'Invalid date object {date_obj} cannot be formatted '
                         f'as a date string.')


def get_default_projects_path() -> str:
    """
    Get the absolute path to the default directory where project databases are
    stored.

    Returns:
        The path.
    """

    return get_data(os.path.join('sqlite', 'projects'))
