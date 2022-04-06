import os.path

from spotiviz import get_data
from spotiviz.projects import manager
from spotiviz.utils import db
from spotiviz.utils.log import LOG
from spotiviz.projects import utils as ut
from spotiviz.projects import sql


def enforce_project_exists(project: str):
    """
    Ensure that the given project exists. If it does not exist, a ValueError
    is raised. If it does exist, nothing happens.

    Args:
        project: The name of the project to check.

    Raises:
        ValueError: If the project does not exist.

    """
    if not does_project_exist(project):
        raise ValueError('Unrecognized project name {p}'.format(p=project))


def does_project_exist(name: str) -> bool:
    """
    Check whether a project with the given name already exists.

    This is done by ensuring that it has a database file and is present in
    the main program database. If the project exists in one of those
    locations but not the other, it is added to the missing location and True
    is returned.

    Note that the name is case in-sensitive and ignores some characters. See
    clean_project_name() for more information on this behaviour.

    :param name: the name of the project to check
    :return: true if project exists
    """

    # TODO I suspect this doesn't work if one project 'abC d' is created and
    #  then another project 'abcd' is created. The second one will find a
    #  database but no sql entry and it'll try to make a second sql entry for
    #  the same database which is already in use by 'abC d'.

    # Check whether a database with this project name (cleaned) exists
    db_exists = os.path.isfile(
        get_data(os.path.join('sqlite', 'projects',
                              ut.clean_project_name(name)))
    )

    # Check whether there's a project entry with this name (not cleaned) in the
    # Projects table
    with db.get_conn() as conn:
        entry_exists = bool(
            conn.execute(sql.CHECK_PROJECT_EXISTS, (name,)).fetchone())

    # If the entry exists but not the database, make the database
    if entry_exists and not db_exists:
        LOG.debug('Project {p} missing database; making it...'.format(p=name))
        manager.create_project_database(name)

    # If the database exists but not the entry, add the entry
    if db_exists and not entry_exists:
        LOG.debug('Project {p} missing sql entry; adding it...'.format(p=name))
        manager.create_project_entry(name)

    # If either the database or entry previously existed (in which case they
    # both exist now), return true. If neither exist, return false
    return db_exists or entry_exists
