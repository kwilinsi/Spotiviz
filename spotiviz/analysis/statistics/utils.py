import os

from spotiviz import get_resources

__STATISTICS_DIR = get_resources(os.path.join('sql', 'statistics'))


def get_file(file: str) -> str:
    """
    Get the path to a statistic resource file specified by the file name.

    Args:
        file: The file name to search for in the resources/sql/statistics
              folder.

    Returns:
        The full path to the file.
    """

    return os.path.join(__STATISTICS_DIR, file)
