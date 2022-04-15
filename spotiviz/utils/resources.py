import os.path

from spotiviz import get_resources


def get_sql_resource(file: str) -> str:
    """
    Get the absolute file path to the specified .sql file in the sql
    constants directory.

    Args:
        file: The desired file.

    Returns:
        An absolute path to that file.
    """

    return get_resources(os.path.join('sql', file))


def get_gui_resource(file: str) -> str:
    """
    Get the absolute file path to the specified GUI resource.

    Args:
        file: The desired file.

    Returns:
        An absolute path to that file.
    """

    return get_resources(os.path.join('gui', file))


def read(path: str) -> str:
    """
    Read the entire contents of some resource file to a string and return it.
    This is commonly paired with other resource methods to locate a file and
    obtain its contents.

    Args:
        path: The path to the file.

    Returns:
        The contents of the file as a string.
    """

    with open(path) as p:
        return p.read()
