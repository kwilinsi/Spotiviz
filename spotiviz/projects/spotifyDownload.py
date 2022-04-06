import json
import os
from typing import List

from spotiviz.projects import fileType as ft, sql
from spotiviz.utils import db
from spotiviz.utils.log import LOG
from spotiviz.projects import manager
from spotiviz.projects import utils


class SpotifyDownload:
    """
    This class represents a collection of downloaded Spotify data. It is
    created by passing a path to a directory that contains data from a single
    Spotify download, and that directory is indexed to identify the relevant
    json files.
    """

    def __init__(self, project: str, path: str, name: str = None):
        """
        Initialize a Spotify download instance by specifying the project to
        which it is attached and the path to a directory containing a single
        instance of downloaded Spotify data.

        If the given project name is invalid (e.g. it doesn't exist) or the
        given path does not resolve to a valid Spotify download directory,
        an exception will be thrown.

        After creating a SpotifyDownload instance, be sure to call the save()
        method to store its contents in the database for the parent project.

        Args:
            project: the project to which this download instance is attached.
            path: the path to the Spotify data download.
            name: the name to assign the download (or omit to set it to the
            bottom-level directory in the path).

        Raises:
            NotADirectoryError: If the path does not point to a valid directory.
            ValueError: If the given project name does not match any existing
                project, or if the path points to a directory that does not
                contain a Spotify download.
        """

        # Make sure the project is valid
        if not manager.is_project_exists(project):
            raise ValueError('Invalid project name: {p}'.format(p=project))

        # Make sure that the path points to a directory
        if not os.path.isdir(path):
            raise NotADirectoryError('Invalid download path {p}'.format(p=path))

        self.path = path
        self.project = project

        # Set the download name
        if name is None:
            self.name = os.path.basename(path)
        else:
            self.name = name

        # Index the files in the download for later
        self.__index()

        # Validate the directory contents to make sure it's a Spotify download
        if not self.isValidDownload():
            raise ValueError(
                'Invalid path (not a Spotify download): {p}'.format(p=path))

        # Print a debug message that the download was created
        LOG.debug('Created download instance at \'{p}\''.format(
            p=path
        ))
        LOG.debug('  Indexed {c} files'.format(c=len(self.files)))

    def __index(self):
        """
        Go through all the files in the path associated with this Spotify
        Download. Add each file to an array of tuples, paired with its file
        type.
        """

        self.files = [(file, ft.getFileType(file))
                      for file in os.listdir(self.path)]

    def isValidDownload(self) -> bool:
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
        for (f, t) in self.files:
            # If any files types are recognized (not unknown), return True
            if t != ft.FileType.UNKNOWN:
                return True
        return False

    def __getStreamingHistories(self) -> List[str]:
        """
        Filter the list of files associated with this download and return the
        ones typed as StreamingHistory files.

        Returns:
             A list of file names (not full paths)
        """

        return [f for f, t in self.files if t == ft.FileType.STREAMING]

    def __getFullPath(self, file) -> str:
        """
        Get the full path to a file based on its name. The name is appended
        to the root path of this download instance.

        Args:
            file: The name of the file.

        Returns:
            The full path to the file.
        """

        return os.path.join(self.path, file)

    def save(self):
        """
        Add information pertaining to this download to the database for the
        parent project. This includes:

        1. Adding the data from this SpotifyDownload to the SQLite
        Downloads table for the project.
        2. Adding each of the streaming history files to the StreamingHistories
        table.
        3. Adding each of the streams (an individual listen to a song at a
        specific time) to the StreamingHistoryRaw table.

        In all cases, duplicate additions to the database are ignored.
        """

        # Open a connection to the database for the parent project
        with db.get_conn(utils.clean_project_name(self.project)) as conn:
            # Add the path for this Download to the database
            conn.execute(sql.ADD_DOWNLOAD, (self.path, self.name))
            download_id = db.get_last_id(conn)

            LOG.debug('Project {p} added Download {d}'.format(p=self.project,
                                                              d=self.path))

            # TODO somehow need to make sure this traverses the streaming
            #  histories in their chronological order, even if that's not the
            #  order they were added to the project. A Spotify download from
            #  December must be processed after one from June.
            #  Actually, I might even need to add a column to the
            #  StreamingHistories table with the first date found in that
            #  streaming history. Then with a left join, I can use that as the
            #  method of ordering in the big select query that produces the
            #  StreamingHistory table. Right now it orders based on
            #  history_id, which is reflective of the order downloads were
            #  added, and that's problematic.

            # For each of the streaming history files...
            for f in self.__getStreamingHistories():
                # Open the streaming file and parse the json
                file = open(self.__getFullPath(f), encoding='utf-8')
                j = json.load(file)
                file.close()

                start_time = j[0]['endTime']

                # Add the file name to the database
                conn.execute(sql.ADD_STREAMING_HISTORY,
                             (download_id, f, start_time))
                history_id = db.get_last_id(conn)

                position = 0
                # Add each stream from each streaming history file to database
                for listen in j:
                    position += 1
                    conn.execute(sql.ADD_RAW_STREAM, (history_id,
                                                      position,
                                                      listen['endTime'],
                                                      listen['artistName'],
                                                      listen['trackName'],
                                                      listen['msPlayed']))

            # Set the Download's start time to the minimum start time found
            # in the streaming history files
            conn.execute(sql.UPDATE_DOWNLOAD_TIME, (download_id, download_id))
