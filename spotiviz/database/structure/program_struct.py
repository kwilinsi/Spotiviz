"""
This models the SQLite database structure for the main Spotiviz program-level
database.
"""

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import func

from spotiviz.database.structure.template import ReprModel

Base = declarative_base()


class Projects(Base, ReprModel):
    __tablename__ = "Projects"
    name = Column(Text, primary_key=True)
    database_path = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return self._repr(id=self.id,
                          name=self.name,
                          database_path=self.database_path,
                          created_at=self.created_at)
