from enum import Enum
from typing import Any


class _Property:
    def __init__(self,
                 friendly_name: str,
                 description: str,
                 data_type: type,
                 default):
        self.friendly_name = friendly_name
        self.data_type = data_type
        self.description = description
        self.default = default


class Config(Enum):
    """
    This is a list of all the configuration settings that belong to each
    project. Each of these is listed in the project's Config table in the
    SQLite database file.
    """

    def cast(self, val: str) -> Any:
        """
        Cast some value from a string (as it is stored in the SQLite
        database) into the appropriate data type for the property.

        Args:
            val: The value to cast.

        Returns:
            The value cast to the appropriated data type.
        """

        return self.value.data_type(val)

    MIN_NON_SKIP_TRACK_LENGTH = _Property(
        'Minimum non-skip track length',
        'The minimum duration a track must play for in order for it not to be '
        'counted a skip (assuming no duration has a frequency of 2 or more). '
        'This is given in milliseconds.',
        int,
        10000
    )

    MIN_NON_SKIP_FREQUENCY_THRESHOLD = _Property(
        'Minimum non-skip frequency threshold',
        'If a track is played for a certain number of milliseconds at least '
        'this many times, and if that duration comprises at least the '
        'MIN_NON_SKIP_FREQUENCY_PERCENT_THRESHOLD, that duration will not be '
        'considered a skip.\n\n'
        'For example, consider song A, which was played 5 times for exactly 1 '
        'minute. If this setting were 5, song A at 1 minute would meet the '
        'threshold. But if song A were only played for 1 minute 4 times, '
        'it wouldn\'t meet the threshold.\n\n'
        'Typically, this value is 2, because it\'s unlikely that a song will '
        'be skipped at exactly the same millisecond duration twice in a row.',
        int,
        2
    )

    MIN_NON_SKIP_FREQUENCY_PERCENT_THRESHOLD = _Property(
        'Non-skip frequency percent threshold',
        'See MIN_NON_SKIP_FREQUENCY_THRESHOLD. That determines the minimum '
        'number of times a song must be played at a certain duration. This '
        'is an additional requirement for what percentage of the total '
        'listens those must comprise.\n\n'
        'If a song is played 1000 times, it\'s likely that it will be skipped '
        'twice (or even more) at exactly the same millisecond mark. This '
        'requires a certain percentage of all the listens to that song to be '
        'at that exactly millisecond mark, in order for it to not be '
        'considered a skip.',
        float,
        0.1
    )

    ABSOLUTE_NON_SKIP_FREQUENCY_THRESHOLD = _Property(
        'Absolute non-skip frequency threshold',
        'If a song is played at a certain duration this many times, it will '
        'never be considered a skip. If this threshold is met, then the '
        'MIN_NON_SKIP_FREQUENCY_PERCENT_THRESHOLD does NOT need to be met for '
        'the song to be marked non-skip.',
        float,
        6
    )

    SKIP_DURATION_ERROR_MARGIN = _Property(
        'Skip duration error margin',
        'As long as a duration is at least this percent less than another '
        'duration that was marked NON_SKIP, this one will also be marked '
        'NON_SKIP.\n\n'
        'For example, if one duration is 100 seconds, and it\'s marked '
        'NON_SKIP, then any duration of at least 98 seconds will also be '
        'marked NON_SKIP (at a 2% error margin).',
        float,
        0.02
    )


def config_from_name(name: str) -> Config:
    """
    Get a Config property by its name, which is the string representation
    used to store config elements in each project's SQLite database file.

    Args:
        name: The name of the property.

    Returns:
        The Config property with that name.

    Raises:
        ValueError: If there is no property with the given name, or the
                    name is None.
    """

    if name is None or not isinstance(name, str):
        raise ValueError(f'Invalid property name {name}.')

    for p in Config:
        if p.name == name:
            return p

    raise ValueError(f'Unrecognized property name {name}.')
