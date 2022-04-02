import re


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