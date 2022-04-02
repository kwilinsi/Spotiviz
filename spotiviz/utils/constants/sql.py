"""
This file contains only a set of SQL constants for referencing scripts and
databases. It intentionally does not depend on any other files in the
Spotiviz package, thereby allowing it to be imported from anywhere.
"""

# The name of the main database with the spotiviz installation data
DATABASE_PROGRAM_NAME = 'program.db'

# The setup script for initializing the main database
SCRIPT_SETUP = 'setup.sql'

GET_LAST_ID = 'SELECT last_insert_rowid();'