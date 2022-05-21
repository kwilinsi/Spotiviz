import os.path
from enum import Enum
from sqlalchemy import select

from spotiviz.database import db
from spotiviz.database.structure.program_struct import Projects
from spotiviz.projects import sql, utils as ut


class ProjectState(Enum):
    # A project is undefined if it isn't listed in the Projects table
    UNDEFINED = 0

    # A project exists if it's in the Projects table and has a database file
    EXISTS = 1

    # A project is given this state if it is listed in the Projects table, but
    # its database file can't be found for some reason.
    MISSING_DATABASE = 2


def enforce_project_exists(project: str) -> None:
    """
    Ensure that the given project exists by checking its ProjectState
    according to checks.project_state(). If it does not fully exist (meaning
    its undefined or missing a database) then a ValueError is raised. If it
    does exist, nothing happens.

    Args:
        project: The name of the project to check.

    Returns:
        None

    Raises:
        ValueError: If the project does not fully exist.

    """

    state = project_state(project)
    if state == ProjectState.UNDEFINED:
        raise ValueError("Unrecognized project name '{p}'".format(p=project))
    elif state == ProjectState.MISSING_DATABASE:
        raise ValueError("Project '{p}' missing database".format(p=project))


def project_state(name: str) -> ProjectState:
    """
    Check whether a project with the given name already exists.

    This is done by ensuring that it has a database file and is present in
    the main program database. If the project exists in one of those
    locations but not the other, it is added to the missing location and True
    is returned.

    Note that the name is case in-sensitive and ignores some characters. See
    clean_project_name() for more information on this behaviour.

    Args:
        name: The name of the project to check.

    Returns:
        True if project exists; otherwise False.
    """

    # Check whether there's a project entry with this name (not cleaned) in the
    # Projects table
    with db.program_session() as session:
        result = session.scalars(
            select(Projects.name).where(Projects.name == name))

        # If there is no entry, the project doesn't exist. Return UNDEFINED.
        if not result.all():
            return ProjectState.UNDEFINED

    # If there is an entry, get the database path
    path = ut.get_database_path(name)

    # If the path exists, the project fully exists. Otherwise, mark its state
    # as missing the database file
    if os.path.isfile(path):
        return ProjectState.EXISTS
    else:
        return ProjectState.MISSING_DATABASE
