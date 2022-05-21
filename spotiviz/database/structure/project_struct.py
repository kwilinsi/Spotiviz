"""
This models the SQLite database structure for each project database file.
"""

from sqlalchemy import (
    Column, Integer, Date, DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base

from spotiviz.database.structure.template import ReprModel

Base = declarative_base()


class Downloads(Base, ReprModel):
    """
    The Downloads table contains a list of Spotify downloads.

    Each download has a unique, auto-incrementing ID; a path to the download's
    folder; a name; and a start date.
    """
    __tablename__ = "Downloads"

    # This implicitly auto-increments in SQLite
    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    start_time = Column(DateTime)
    download_date = Column(Date)

    def __repr__(self) -> str:
        return self._repr(id=self.id,
                          path=self.path,
                          name=self.name,
                          start_time=self.start_time,
                          download_date=self.download_date)


class StreamingHistories(Base, ReprModel):
    """
    The StreamingHistories table contains a list of streaming history files.

    Each streaming history file is associated with a specific download,
    specified by its id. The file is given only by its name (e.g.
    StreamingHistory0.json), which is appended to the download's path to get
    the full path to the history file. This also includes a timestamp for the
    first listen in the streaming history.
    """
    __tablename__ = "StreamingHistories"
    __table_args__ = (UniqueConstraint('download_id', 'file_name'),)

    # This implicitly auto-increments in SQLite
    id = Column(Integer, primary_key=True)
    download_id = Column(Integer, ForeignKey('Downloads.id'), nullable=False)
    file_name = Column(Text, nullable=False)
    start_time = Column(DateTime)
    download_date = Column(Date)

    def __repr__(self) -> str:
        return self._repr(id=self.id,
                          path=self.path,
                          name=self.name,
                          start_time=self.start_time,
                          download_date=self.download_date)
