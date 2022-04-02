from spotiviz.utils import resources as re
from spotiviz.utils import db
from spotiviz.utils.constants import sql
from spotiviz.utils.log import LOG
from spotiviz.projects import manager


def install_spotiviz():
    """
    Install the Spotiviz application. This primarily entails the creation of
    a database for storing projects.
    """

    LOG.debug('Starting Spotiviz installation')

    # Run installation script
    LOG.debug('Running installation script')
    db.run_script(re.get_sql_resource(sql.SCRIPT_SETUP))

    # Delete any leftover projects
    manager.delete_all_projects()
