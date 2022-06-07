"""
This models the SQLite database structure for the main Spotiviz program-level
database.
"""

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import TEXT, DATETIME, BOOLEAN
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import func

from spotiviz.database.structure.template import ReprModel

Base = declarative_base()


class Projects(Base, ReprModel):
    """
    This table stores a list of all the projects associated with this
    Spotiviz installation. They are stored along with the path to their
    SQLite database files for loading in the future.
    """

    __tablename__ = "Projects"

    name: Column = Column(TEXT, primary_key=True)
    database_path: Column = Column(TEXT, nullable=False)
    created_at: Column = Column(DATETIME, nullable=False,
                                server_default=func.now())

    def __repr__(self) -> str:
        return self._repr(name=self.name,
                          database_path=self.database_path,
                          created_at=self.created_at)


class Config(Base, ReprModel):
    """
    This tables stores both global configuration settings for the entire
    Spotiviz installation, along with the default project configuration for
    new projects.
    """

    __tablename__ = 'Config'

    key: Column = Column(TEXT, primary_key=True)
    value: Column = Column(TEXT)
    is_project_default: Column = Column(BOOLEAN, nullable=False)

    def __repr__(self) -> str:
        return self._repr(key=self.key,
                          value=self.value)
