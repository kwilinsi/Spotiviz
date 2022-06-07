import enum


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

    def to_str(self, value=None):
        """
        Convert some value for this property to a string. For example,
        5 would be converted to '5'. If no value is provided, the default
        value is converted instead.

        Args:
            value: [Optional] the value to convert.

        Returns:
            The string representation of the given (or default) value.
        """

        if value:
            return str(value)
        else:
            return str(self.default)


class Config(enum.Enum):
    """
    This is a list of all the configuration settings that belong to each
    project. Each of these is listed in the project's Config table in the
    SQLite database file.
    """

    MIN_NON_SKIP_TRACK_LENGTH = _Property(
        'Minimum non-skip track length',
        'The minimum duration a track must play for in order for it not to be '
        'counted a skip (assuming no duration has a frequency of 2 or more). '
        'This is given in milliseconds.',
        int,
        10000
    )

    MIN_NON_SKIP_FREQUENCY_PERCENT_THRESHOLD = _Property(
        'Non-skip frequency percent threshold',
        'See MIN_NON_SKIP_TRACK_LENGTH.',
        float,
        0.1
    )

    ABSOLUTE_NON_SKIP_FREQUENCY_THRESHOLD = _Property(
        'Absolute non-skip frequency',
        'If any song was played for a certain duration at least this number '
        'of times, it will never be counted as a skip. It\'s simply highly '
        'unlikely for that to happen.',
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
