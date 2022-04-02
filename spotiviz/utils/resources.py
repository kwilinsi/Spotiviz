import os.path

from spotiviz import get_resources


def get_sql_resource(file: str) -> str:
    """
    Get the absolute file path to the specified .sql file in the sql
    constants directory.

    :param file: the desired file
    :return: an absolute path to that file
    """

    return get_resources(os.path.join('sql', file))
