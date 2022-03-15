import os
import sqlite3

import src.database.resources as resc
from src.utils.log import LOG

DATABASE_FILE = os.path.join(resc.DATA_DIRECTORY, 'spotify.db')


def install():
    LOG.debug('Creating database at: {path}'.format(path=DATABASE_FILE))
    conn = sqlite3.connect(DATABASE_FILE)

    with open(resc.SQL_INSTALL_SCRIPT) as installScript:
        conn.executescript(installScript.read())

    LOG.debug('Initialized database')
