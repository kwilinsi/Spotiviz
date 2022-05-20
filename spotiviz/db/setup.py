"""
This populates the main Spotiviz program-level database with the appropriate
Tables and Views.
"""

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import func
from spotiviz import db

Base = declarative_base()


class Projects(Base):
    __tablename__ = "Projects"
    name = Column(Text, primary_key=True)
    database_path = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"Projects(name={self.name!r}, " \
               f"database_path={self.database_path!r}, " \
               f"created_at = {self.created_at!r})"


Base.metadata.create_all(db.GLOBAL_ENGINE)
