import os.path

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_resources(path: str = None) -> str:
    """
    Get a complete path to the specified resource in the resources directory.
    The specified path, if given, is joined to an absolute root path of the
    spotiviz directory along with a reference to the resources directory.

    If no path is given, an absolute reference to the root of the
    resources directory is returned.

    :param path: a path to the desired file within the resources directory
    :return: the full absolute path to that data file
    """

    if path is None:
        return os.path.join(_ROOT, 'resources')
    else:
        return os.path.join(_ROOT, 'resources', path)


def get_data(path: str = None) -> str:
    """
    Similar to get_resources, this returns a complete path to the specified
    file in the data directory.

    If no path is given, an absolute reference to the root of the data
    directory is returned.

    :param path: a path to the desired file within the data directory
    :return: the full absolute path to that data file
    """

    if path is None:
        return os.path.join(_ROOT, 'data')
    else:
        return os.path.join(_ROOT, 'data', path)
