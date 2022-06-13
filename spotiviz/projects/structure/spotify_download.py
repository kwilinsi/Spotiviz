from __future__ import annotations

import os
from typing import Dict, List, Tuple
from datetime import date

from sqlalchemy import func, select

from spotiviz.utils.log import LOG

from spotiviz.database.structure.project_struct import (
    Downloads, StreamingHistories, StreamingHistoryRaw
)

from spotiviz.projects import utils as ut
from spotiviz.projects.structure import fileType as ft
from spotiviz.projects.structure import (
    project_class as pc, generic_file as gf, streaming_history as sh
)


class SpotifyDownload:
    """
    This class represents a collection of downloaded Spotify data. It is
    created by passing a path to a directory that contains data from a single
    Spotify download, and that directory is indexed to identify the relevant
    json files.
    """

    def __init__(self,
                 project: pc.Project,
                 path: str,
                 name: str = None,
                 download_date: date = None,
                 download_id: int = -1,
                 index: bool = False,
                 loaded: bool = False):

        """
        Initialize a SpotifyDownload instance by specifying the project to
        which it is attached and the path to a directory containing a single
        instance of downloaded Spotify data.

        If the given project name is invalid (e.g. it doesn't exist) or the
        given path does not resolve to a valid Spotify download directory,
        an exception will be thrown.

        After creating a SpotifyDownload instance, be sure to call the
        save_to_database() method to store its contents in the database for
        the parent project.

        Args:
            project: The project to which this download instance is attached.
            path: The path to the Spotify data download.
            name: The name to assign the download (or omit to set it to the
                  bottom-level directory in the path).
            download_date: [Optional] The date that the download was requested
                           from Spotify.
            index: Whether the contents of this download should be indexed
                   immediately. Set this to True if you don't know for sure
                   that the directory is actually a Spotify download.
            loaded: Whether the contents of this download have already been
                    loaded into the SQLite database. If this true, index should
                    almost certainly be marked false.

        Raises:
            NotADirectoryError: If the path does not point to a valid directory.
            ValueError: If the path points to a directory that does not
                        contain a Spotify download. (This is only possible if
                        the 'index' parameter is True).
        """

        # Make sure that the path points to a directory
        if not os.path.isdir(path):
            raise NotADirectoryError(f'Invalid download path \'{path}\'')

        # Initialize basic attributes
        self.path: str = path
        self.project: pc.Project = project
        self.date: date = download_date
        self.name: str = os.path.basename(path) if name is None else name
        self.files: Dict[str, Tuple[ft.FileType, gf.GenericFile]] = {}
        self.loaded: bool = loaded

        # Set a temporary id for this download
        self.id: int = download_id

        # Index the files in the download for later
        if index:
            self.index()

            # Validate the directory contents to make sure it's a Spotify
            # download
            if not self.is_valid_download():
                raise ValueError(f'Invalid path (not Spotify '
                                 f'download): \'{path}\'')

        # Print a debug message that the download was created
        LOG.debug(f'Created download instance at \'{path}\'')

        if index:
            LOG.debug(f'  Indexed {len(self.files)} files')

    @classmethod
    def from_sql(cls,
                 project: pc.Project,
                 download_record: Downloads) -> SpotifyDownload:
        """
        Create a SpotifyDownload instance from an instance of the
        SQLAlchemy-based Downloads class, which represents a record in the
        Downloads table in the project database.

        For more information, see project_class.Project.from_sql().

        Args:
            project: To the project to which this download belongs.
            download_record: A record in the SQL database form the Downloads
                             table.

        Returns:
            A new SpotifyDownload instance.
        """

        return cls(project,
                   download_record.path,
                   download_record.name,
                   download_record.download_date,
                   download_record.id,
                   index=False,
                   loaded=False)

    def __str__(self) -> str:
        """
        Get the string representation of this download (the project name and
        the download path each in single quotes).

        Returns:
            A string for this download.
        """

        return f'{self.project} download \'{self.path}\''

    def index(self) -> None:
        """
        Go through all the files in the path associated with this Spotify
        Download. Add each file to a dictionary `self.files`, where the file
        name is the key. Each value is a tuple of the file type and an object
        created from that file, if applicable.

        Returns:
            None
        """

        for file in os.listdir(self.path):
            t = ft.getFileType(file)

            # If it's a streaming history file, create an object
            if t == ft.FileType.STREAMING:
                o = sh.StreamingHistory(self.project, self, file)
            else:
                o = gf.GenericFile(self.project, self, file)

            self.files[file] = (t, o)

    def is_valid_download(self) -> bool:
        """
        Determine whether this is a valid Spotify Download based on the
        contents of its directory.

        A download is considered valid if it contains at least ONE file of a
        recognized type (streaming history, library, etc.).

        If any of these files are found, True is returned. Otherwise,
        False is returned.

        Returns:
            True if and only if the path associated with this download
            contains at least one recognized Spotify data file.
        """

        # Iterate through each of the indexed files
        for file in self.files:
            # If any files types are recognized (not unknown), return True
            if self.files[file][0] != ft.FileType.UNKNOWN:
                return True
        return False

    def __get_streaming_histories(self) -> List[sh.StreamingHistory]:
        """
        Filter the list of files associated with this download to find the
        StreamingHistory ones and return those objects.

        Returns:
             A list of StreamingHistory objects mapped to individual files.
        """

        # noinspection PyTypeChecker
        return [self.files[file][1] for file in self.files
                if self.files[file][0] == ft.FileType.STREAMING]

    def get_full_path(self, file) -> str:
        """
        Get the full path to a file based on its name. The name is appended
        to the root path of this download instance.

        Args:
            file: The name of the file.

        Returns:
            The full path to the file.
        """

        return os.path.join(self.path, file)

    def to_sql_object(self) -> Downloads:
        """
        Create a SQLAlchemy object of this SpotifyDownload based on the
        Downloads class from spotiviz.database.structure.project_struct.py.

        Returns:
            The SQL object with the appropriate parameters.
        """

        # noinspection PyArgumentList
        return Downloads(path=self.path,
                         name=self.name,
                         download_date=self.date)

    def save_to_database(self) -> None:
        """
        Add this Spotify download to the Downloads table in the SQLite
        database for the project. Note that this does NOT add the contents of
        the files in the download to the database. For that, you must call
        self.load().

        Returns:
            None
        """

        # Open a connection to the database for the parent project
        with self.project.open_session() as session:
            # Add the path for this Download to the database
            d = self.to_sql_object()
            session.add(d)
            session.commit()
            self.id = d.id

        LOG.debug(f'Added to project {self} with id {self.id}')

    def load(self) -> None:
        """
        This function saves the contents of the files in this Spotify
        download to the SQLite database for the project. Currently, it performs
        the following actions.

        1. Add each of the streaming history files to the StreamingHistories
        table.

        2. Add each of the streams (an individual listen to a song at a
        specific time) to the StreamingHistoryRaw table.

        3. Call self.__set_download_date() to set the download date for this
           project based on the streaming history, if it was not already
           provided by the user.

        4. Update self.loaded to True.

        Important: This must be called AFTER the download directory is
        indexed via self.index(). This is performed automatically in the
        __init__ method, provided that the index parameter is True.

        Returns:
            None
        """

        # Add each StreamingHistory file (and its contents) to the database
        for f in self.__get_streaming_histories():
            f.save_to_database()

        with self.project.open_session() as session:
            # Get the minimum start time found in the streaming history files
            min_time = session.scalars(
                select(func.min(StreamingHistories.start_time))
                    .where(StreamingHistories.download_id == self.id)).one()

            # Set this download's minimum start time
            this_download = session.scalars(
                select(Downloads).where(Downloads.id == self.id)).one()
            this_download.start_time = min_time

            session.commit()

        # Validate/set the download date
        self.__set_download_date()

        self.loaded = True
        with self.project.open_session() as session:
            stmt = select(Downloads).where(Downloads.id == self.id)
            me = session.scalars(stmt).one()
            me.loaded = True
            session.commit()

    def __set_download_date(self) -> None:
        """
        Set the download_date associated with this download in the Downloads
        table. That date should represent the date that the download was
        requested from Spotify. Typically, it is provided by the user when
        they create a SpotifyDownload object.

        However, it's possible that the provided download_date is wrong,
        or that no date was given. If the last end_time for this Download is
        AFTER the user-provided download_date, the user-provided date is
        obviously wrong. In this case, or if the user simply does not provide
        a date, the download_date is set to the last recorded end_time from the
        streaming histories.

        Note that if the last end_time is BEFORE the user-provided
        download_date, this doesn't mean anything is wrong. The user may
        simply have not listened to Spotify a few days before requesting
        their data.

        Returns:
            None

        Raises:
            AssertionError: If querying the StreamingHistoryRaw table fails
                            for some reason (e.g. it's empty and no end_date
                            can be found).
        """

        with self.project.open_session() as session:
            # Get the last end time
            stmt = (
                select(func.max(StreamingHistoryRaw.end_time))
                    .join(StreamingHistoryRaw.streaming_history)
                    .where(StreamingHistories.download_id == self.id)
            )

            # Get the end date
            end_date = session.scalars(stmt).one()

        if not end_date:
            print(f'end_date: {end_date} with type: {type(end_date)}')
            raise AssertionError(f'Failed to query StreamingHistoryRaw '
                                 f'table for project {self.project}. '
                                 f'Is it empty?')

        # Remove time (hours/seconds) from date:
        end_date = end_date.date()

        if self.date is None:
            self.date = end_date
        elif self.date < end_date:
            LOG.warn(
                f'User-provided end date {ut.date_to_str(self.date)} is '
                f'before last recorded listen date {ut.date_to_str(end_date)} '
                f'for {self}. Overriding user-provided date.')
            self.date = end_date
        else:
            return

        # If this point is reached, the date changed. Update it in SQL.
        d = session.scalars(
            select(Downloads).where(Downloads.id == self.id)).one()
        d.download_date = end_date
        session.commit()
