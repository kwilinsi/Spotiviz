import datetime
from enum import Enum
from typing import Iterable, Tuple, Dict
import os.path
import sqlite3

from spotiviz.analysis.statistics import utils as ut
from spotiviz.utils import db
from spotiviz.projects import checks, utils as proj_ut


class StatType(Enum):
    """
    These are the various return types that a statistic can take.
    """

    INT = 0
    FLOAT = 1
    DATE = 2


class Statistic(Enum):
    """
    This enum class stores references to each of the statistics SQL files in
    the resources directory. Detailed documentation for each of the statistics
    can be found in their respective SQL files.
    """

    # ARTIST AND TRACK COUNTS
    ARTIST_COUNT = (
        'artist_count',
        ut.get_file('artist_count.sql'),
        StatType.INT
    )

    TRACK_COUNT = (
        'track_count',
        ut.get_file('track_count.sql'),
        StatType.INT
    )

    # LISTEN TIME

    HOURS_TOTAL = (
        'hours_total',
        ut.get_file('hours_total.sql'),
        StatType.INT
    )

    AVG_LISTEN_TIME_OVERALL = (
        'avg_listen_time_overall',
        ut.get_file('avg_listen_time_overall.sql'),
        StatType.FLOAT
    )

    AVG_LISTEN_TIME_FILTERED = (
        'avg_listen_time_filtered',
        ut.get_file('avg_listen_time_filtered.sql'),
        StatType.FLOAT
    )

    # DATE RANGES

    DATE_MIN = (
        'date_min',
        ut.get_file('date_min.sql'),
        StatType.DATE
    )

    DATE_MAX = (
        'date_max',
        ut.get_file('date_max.sql'),
        StatType.DATE
    )

    DATE_PRESENT = (
        'date_present',
        ut.get_file('date_present.sql'),
        StatType.INT
    )

    DATE_RANGE = (
        'date_range',
        ut.get_file('date_range.sql'),
        StatType.INT
    )

    DATE_LISTENED = (
        'date_listened',
        ut.get_file('date_listened.sql'),
        StatType.INT
    )


def get_stats(connection: sqlite3.Connection) -> Iterable[Tuple[str, object]]:
    """
    Yield an iterator over each of the statistics in the Statistic enumerated
    class.

    Args:
        connection: A SQLite connection to the database on which to execute
                    each of the statistic queries.

    Returns:
        The path and value for each statistic.
    """

    for s in Statistic:
        name, path, stat_type = s.value
        with open(path) as p:
            result = connection.execute(p.read()).fetchone()[0]

        if stat_type == StatType.INT:
            yield name, int(result)
        elif stat_type == StatType.FLOAT:
            yield name, float(result)
        elif stat_type == StatType.DATE:
            yield name, proj_ut.to_date(result)


def get_stats_dict(project: str) -> Dict:
    """
    Calculate a series of summary statistics for a given project, and return
    it as a dictionary.

    Args:
        project: The project to calculate statistics for.

    Returns:
        None

    Raises:
        ValueError: If the given project name is invalid or the project
                    doesn't exist.
    """

    # Ensure the project exists first
    checks.enforce_project_exists(project)

    # Create the statistics dictionary
    s = dict()

    with db.get_conn(proj_ut.clean_project_name(project)) as conn:
        for name, value in get_stats(conn):
            s[name] = value

    return s


def print_stats(project: str, stats_dict: Dict) -> None:
    """
    Print the summary statistics from a project to the console. This is mostly
    used for testing and debugging purposes.

    Args:
        project: The name of the project (only used for displaying in the
                 console).
        stats_dict: A dictionary of summary statistics, such as that generated
                    by get_stats_dict().

    Returns:
        None
    """

    print('Project:', project)
    print()
    for s in stats_dict:
        value = stats_dict[s]
        if type(value) is datetime.datetime:
            v = proj_ut.date_to_str(value)
        else:
            v = str(value)

        print('{stat}: {val}'.format(stat=s, val=v))
