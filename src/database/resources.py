import os.path

# The current working directory is assumed to be the installation location
INSTALLATION_DIRECTORY = os.getcwd()

# Top level data directory that contains the database
DATA_DIRECTORY = os.path.join(INSTALLATION_DIRECTORY, 'data')

# Top level resource directory, inside the installation root
RESOURCES_DIRECTORY = os.path.join(INSTALLATION_DIRECTORY, 'resources')

# The sql resources directory inside the resources directory
SQL_DIRECTORY = os.path.join(RESOURCES_DIRECTORY, 'sql')

# The script to set up the database, inside the sql resource directory
SQL_INSTALL_SCRIPT = os.path.join(SQL_DIRECTORY, 'install.sql')
