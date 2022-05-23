"""
This models the SQLite database structure for each project database file.
"""

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.sqlite import (
    BOOLEAN, DATE, DATETIME, FLOAT, INTEGER, TEXT
)
from sqlalchemy.orm import declarative_base, relationship

from spotiviz.database.structure.template import ReprModel

Base = declarative_base()


class Downloads(Base, ReprModel):
    """
    The Downloads table contains a list of Spotify downloads.

    Each download has a unique, auto-incrementing ID; a path to the download's
    folder; a name; and a start date.
    """

    __tablename__ = 'Downloads'

    # This implicitly auto-increments in SQLite
    id: Column = Column(INTEGER, primary_key=True)
    path: Column = Column(TEXT, nullable=False, unique=True)
    name: Column = Column(TEXT, nullable=False)
    start_time: Column = Column(DATETIME)
    download_date: Column = Column(DATE)

    streaming_histories = relationship('StreamingHistories',
                                       back_populates='download',
                                       cascade='all, delete-orphan')

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

    __tablename__ = 'StreamingHistories'
    __table_args__ = (UniqueConstraint('download_id', 'file_name'),)

    # This implicitly auto-increments in SQLite
    id: Column = Column(INTEGER, primary_key=True)
    download_id: Column = Column(INTEGER, ForeignKey('Downloads.id'),
                                 nullable=False)
    file_name: Column = Column(TEXT, nullable=False)
    start_time: Column = Column(DATETIME)

    download = relationship('Downloads',
                            back_populates='streaming_histories')

    listens = relationship('StreamingHistoryRaw',
                           back_populates='streaming_history',
                           cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return self._repr(id=self.id,
                          path=self.path,
                          name=self.name,
                          start_time=self.start_time,
                          download_date=self.download_date)


class StreamingHistoryRaw(Base, ReprModel):
    """
    The StreamingHistoryRaw table contains all the contents of the streaming
    history files given in the StreamingHistories table.

    Each StreamingHistory#.json file contains a list of Spotify listen records.
    When the files are parsed, each of those listens is stored in this table.
    Note however that this table will likely contain duplicate entries.
    """

    __tablename__ = 'StreamingHistoryRaw'

    history_id: Column = Column(INTEGER, ForeignKey('StreamingHistories.id'),
                                primary_key=True)
    position: Column = Column(INTEGER, primary_key=True)
    end_time: Column = Column(DATETIME, nullable=False)
    artist_name: Column = Column(TEXT, nullable=False)
    track_name: Column = Column(TEXT, nullable=False)
    ms_played: Column = Column(INTEGER, nullable=False)

    streaming_history = relationship('StreamingHistories',
                                     back_populates='listens')

    def __repr__(self) -> str:
        return self._repr(history_id=self.history_id,
                          position=self.position,
                          end_time=self.end_time,
                          artist_name=self.artist_name,
                          track_name=self.track_name,
                          ms_played=self.ms_played)


class Artists(Base, ReprModel):
    """
    The Artists table is simply a list of artist names and ids (for smaller
    storage in other tables). It's used mainly for foreign key references.

    Note that this typically does NOT include an 'Unknown Artist' entry. If a
    listen was 'Unknown Track' by 'Unknown Artist', then that won't put
    'Unknown Artist' in this table. But there are actual artists on Spotify
    with the name 'Unknown Artist'. If there's a listen to a valid track
    name by 'Unknown Artist', then it will appear in this table.
    """

    __tablename__ = 'Artists'

    id: Column = Column(INTEGER, primary_key=True)
    name: Column = Column(TEXT, unique=True, nullable=False)

    tracks = relationship('Tracks',
                          back_populates='artist',
                          cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return self._repr(id=self.id, name=self.name)


class Tracks(Base, ReprModel):
    """
    This is similar to the Artists table, in that it's a list of track with
    a unique id used primarily for foreign key references. It helps with
    grouping by tracks because the group can be performed across only the id
    rather than both the artist and the track name.

    Note that this does NOT include an 'Unknown Track' entry unless a real
    track with that name was streamed. See the Artists table documentation
    for more information.
    """

    __tablename__ = 'Tracks'
    __table_args__ = (UniqueConstraint('artist_id', 'name'),)

    id: Column = Column(INTEGER, primary_key=True)
    artist_id: Column = Column(INTEGER, ForeignKey('Artists.id'))
    name: Column = Column(TEXT, nullable=False)

    artist = relationship('Artists', back_populates='tracks')

    listens = relationship('StreamingHistory',
                           back_populates='track',
                           cascade='all, delete-orphan')

    track_lengths = relationship('TrackLengths',
                                 back_populates='track',
                                 cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return self._repr(id=self.id,
                          artist_id=self.artist_id,
                          name=self.name)


class StreamingHistory(Base, ReprModel):
    """
    The StreamingHistory table is a duplicate of the StreamingHistoryRaw
    table where the duplicate listens have been removed.

    Each listen includes a Spotify track name, the artist name, the number of
    milliseconds spent listening to that song, and the end time that the song
    stopped playing.
    """

    __tablename__ = 'StreamingHistory'

    position: Column = Column(INTEGER, primary_key=True)
    end_time: Column = Column(DATETIME, nullable=False)
    # The track_id is null for 'Unknown Track' by 'Unknown Artist'
    track_id: Column = Column(INTEGER, ForeignKey('Tracks.id'))
    ms_played: Column = Column(INTEGER, nullable=False)

    track = relationship('Tracks', back_populates='listens')

    def __repr__(self) -> str:
        return self._repr(position=self.position,
                          end_time=self.end_time,
                          track_id=self.track_id,
                          ms_played=self.ms_played)


class ListenDates(Base, ReprModel):
    """
    The ListenDates table is used for resolving issues with missing data. It
    contains one entry for every date between the very first and very last
    recorded listen dates in a project.

    Each date is matched with booleans indicating whether there is any listen
    history data present for that date and whether it is known as a missing
    date.

    Missing dates are defined as those that were not captured by any of the
    Spotify downloads associated with a project. Spotify downloads have a
    duration of one year (or less if the Spotify account is newer than that).
    If one download ends January 1st 2020 and another ends February 1st 2022,
    all the dates from 01-02-20 to 01-31-21 will be marked missing, because
    they are not captured in either download.

    Note that any entry where is_missing is TRUE should also list has_listen as
    FALSE. Having no data doesn't *define* missing data, but missing data should
    not have any data.
    """

    __tablename__ = 'ListenDates'

    day: Column = Column(DATE, primary_key=True)
    has_listen: Column = Column(BOOLEAN, nullable=False)
    is_missing: Column = Column(BOOLEAN, nullable=False)

    def __repr__(self) -> str:
        return self._repr(day=self.day,
                          has_lisen=self.has_lisen,
                          is_missing=self.is_missing)


class TrackLengths(Base, ReprModel):
    """
    This is a list of tracks and the amount of time spent listening to them (in
    milliseconds). It stores the frequency of each listen time for each song.
    This is used to help determine which listens were likely skips.

    The skip column stores a single character flag denoting whether that listen
    length for that track should be considered a skip. It can take on the
    following values:
        null - Unassigned state
        S    - Skip
        N    - Not a skip
    """

    __tablename__ = 'TrackLengths'

    track_id: Column = Column(INTEGER, ForeignKey('Tracks.id'),
                              primary_key=True)
    ms_played: Column = Column(INTEGER, primary_key=True)
    frequency: Column = Column(INTEGER, nullable=False)
    percent_listens: Column = Column(FLOAT, nullable=False)
    # Skips are initially null and is filled later with a Python script
    skip: Column = Column(INTEGER)

    track = relationship('Tracks', back_populates='track_lengths')

    def __repr__(self) -> str:
        return self._repr(track_id=self.track_id,
                          ms_played=self.ms_played,
                          frequency=self.frequency,
                          percent_listens=self.percent_listens,
                          skip=self.skip)
