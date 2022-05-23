"""
This models the SQLite database structure for the main Spotiviz program-level
database.
"""

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import TEXT, DATETIME
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import func

from spotiviz.database.structure.template import ReprModel

Base = declarative_base()


class Projects(Base, ReprModel):
    __tablename__ = "Projects"
    name: Column = Column(TEXT, primary_key=True)
    database_path: Column = Column(TEXT, nullable=False)
    created_at: Column = Column(DATETIME, nullable=False,
                                server_default=func.now())

    def __repr__(self) -> str:
        return self._repr(name=self.name,
                          database_path=self.database_path,
                          created_at=self.created_at)
