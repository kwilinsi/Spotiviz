"""
This file contains a set of constants for identifying SQLite databases. Its
only internal dependency is the base spotiviz module, namely the __init__.py
file.
"""

import os.path

from spotiviz import get_data

# The path to the main database with the Spotiviz installation data
DATABASE_PROGRAM_PATH = get_data(os.path.join('sqlite', 'program.db'))

# The setup script for initializing the main database
SCRIPT_SETUP = 'setup.sql'

GET_LAST_ID = 'SELECT last_insert_rowid();'
