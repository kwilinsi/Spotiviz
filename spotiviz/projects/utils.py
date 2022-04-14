import datetime
import re
from datetime import date, timedelta, datetime
from typing import Optional

# This format is used for storing dates in the SQLite database
__DATE_FORMAT = '%Y-%m-%d'


def clean_project_name(name: str) -> str:
    """
    This cleans a project name. It is converted to lowercase, and all
    characters except letters, numbers, hyphens, and underscores are removed.

    This is primarily used for setting the names of database files for each
    project. The project name is not cleaned in the main program database for
    the entire Spotiviz installation.

    This also adds .db to the file name if it was not there initially. Note
    that this is the only . that is allowed in the returned string.

    :param name: the name to clean
    :return: the cleaned name
    """

    n = name.lower()
    return re.sub(r'[^\w-]', '', n[:-3] if n.endswith('.db') else n) + '.db'


def date_range(start_date: date, end_date: date):
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
