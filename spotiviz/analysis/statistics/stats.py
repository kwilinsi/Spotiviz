import datetime
from enum import Enum
from typing import Iterable, Tuple, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from spotiviz.analysis.statistics import utils as ut

from spotiviz.projects import utils as proj_ut
from spotiviz.projects.structure import project_class as pc


class StatType(Enum):
    """
    These are the various return types that a statistic can take.
    """

    INT = 0
    FLOAT = 1
    DATE = 2


class StatUnit(Enum):
    """
    This is the unit that a statistic is given in, which is primarily used
    when printing the unit to the console.
    """

    TRACKS = 'tracks'
    ARTISTS = 'artists'
    HOURS = 'hours'
    DAYS = 'days'
    NONE = ''


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
        StatType.INT,
        StatUnit.ARTISTS
    )

    TRACK_COUNT = (
        'track_count',
        ut.get_file('track_count.sql'),
        StatType.INT,
        StatUnit.TRACKS
    )

    # LISTEN TIME

    HOURS_TOTAL = (
        'hours_total',
        ut.get_file('hours_total.sql'),
        StatType.INT,
        StatUnit.HOURS
    )

    AVG_LISTEN_TIME_OVERALL = (
        'avg_listen_time_overall',
        ut.get_file('avg_listen_time_overall.sql'),
        StatType.FLOAT,
        StatUnit.HOURS
    )

    AVG_LISTEN_TIME_FILTERED = (
        'avg_listen_time_filtered',
        ut.get_file('avg_listen_time_filtered.sql'),
        StatType.FLOAT,
        StatUnit.HOURS
    )

    # DATE RANGES

    DATE_MIN = (
        'date_min',
        ut.get_file('date_min.sql'),
        StatType.DATE,
        StatUnit.NONE
    )

    DATE_MAX = (
        'date_max',
        ut.get_file('date_max.sql'),
        StatType.DATE,
        StatUnit.NONE
    )

    DATE_PRESENT = (
        'date_present',
        ut.get_file('date_present.sql'),
        StatType.INT,
        StatUnit.DAYS
    )

    DATE_RANGE = (
        'date_range',
        ut.get_file('date_range.sql'),
        StatType.INT,
        StatUnit.DAYS
    )

    DATE_LISTENED = (
        'date_listened',
        ut.get_file('date_listened.sql'),
        StatType.INT,
        StatUnit.DAYS
    )


def get_stats(session: Session) -> Iterable[Tuple[StatType, object, StatUnit]]:
    """
    Yield an iterator over each of the statistics in the Statistic enumerated
    class.

    Args:
        session: A SQLAlchemy session connected to the SQLite database
        for the project on which to execute each of the statistic queries.

    Yields:
        Each statistic enum, along with its value and unit.

    Returns:
        An iterator over each statistic enum and its value and unit.
    """

    for s in Statistic:
        name, path, stat_type, unit = s.value
        with open(path) as p:
            result = session.scalars(text(p.read())).one()

        if stat_type == StatType.INT:
            yield s, int(result), unit
        elif stat_type == StatType.FLOAT:
            yield s, float(result), unit
        elif stat_type == StatType.DATE:
            yield s, proj_ut.to_date(result), unit


def get_stats_dict(project: pc.Project) -> Dict:
    """
    Calculate a series of summary statistics for a given project, and return
    it as a dictionary.

    Args:
        project: The project on which to calculate statistics.

    Returns:
        A dictionary of paired statistics, with StatType enums as keys,
        and value-unit tuple pairs as values.

    Raises:
        ValueError: If the given project name is invalid or the project
                    doesn't exist.
    """

    # Create the statistics dictionary
    s = dict()

    with project.open_session() as session:
        for stat_type, value, unit in get_stats(session):
            s[stat_type] = (value, unit)

    return s


def print_stats(project_name: str, stats_dict: Dict) -> None:
    """
    Print the summary statistics from a project to the console. This is mostly
    used for testing and debugging purposes.

    Args:
        project_name: The name of the project (only used for displaying in the
                      console).
        stats_dict: A dictionary of summary statistics, such as that generated
                    by get_stats_dict().

    Returns:
        None
    """

    print('Summary Statistics')
    print('Project:', project_name)
    print()

    for s in stats_dict:
        value, unit = stats_dict[s]
        if type(value) is datetime.datetime:
            v = proj_ut.date_to_str(value)
        else:
            v = str(value)

        print(f'{s.value[0]}: {v} {unit.value}')
