import os
from typing import List

from src.cleaner import fileType
from src.utils.log import LOG


class SpotifyDownload:
    """
    This class represents a collection of downloaded Spotify data. It is
    created by passing a path to a directory that contains data from a single
    Spotify download, and that directory is indexed to identify the relevant
    json files.
    """

    def __init__(self, path: str):
        """
        Initialize a spotify download instance by specifying the path to a
        directory containing a single instance of downloaded Spotify data.

        :param path: the path to the Spotify data download.
        """

        # Set the path for this download
        self.path = path
        LOG.debug('Created download instance at \'{p}\''.format(
            p=path
        ))

        # Index the files in the download
        self.__index()

        # Validate download and log results
        if self.isValidDownload():
            LOG.debug('  Validated download')
        else:
            LOG.debug('  Download validation failed: no recognized files')

    def __index(self):
        """
        Go through all the files in the path associated with this Spotify
        Download. Add each file to an array of tuples, paired with its file
        type.
        """

        self.files = [(file, fileType.getFileType(file))
                      for file in os.listdir(self.path)]

        LOG.debug('  Indexed {c} files'.format(c=len(self.files)))

    def isValidDownload(self) -> bool:
        """
        Determine whether this is a valid Spotify Download based on the
        contents of its directory. If it doesn't contain at least one of the
        recognized file types (streaming history, library, etc.) it is not
        valid, and False is returned. Otherwise, it returns True.

        :return: True if and only if the path associated with this download
        contains at least one recognized Spotify data file.
        """

        # Iterate through each of the indexed files
        for (f, t) in self.files:
            # If any files types are recognized (not unknown), return True
            if t != fileType.FileType.UNKNOWN:
                return True
        return False

    def getStreamingHistories(self) -> List[str]:
        """
        Filter the list of files associated with this download and return the
        ones typed as StreamingHistory files.
        :return: a list of file paths as strings
        """

        return [self.__getFullPath(f) for (f, t) in self.files
                if t == fileType.FileType.STREAMING]

    def __getFullPath(self, file) -> str:
        """
        Get the full path to a file based on its name. The name is appended
        to the root path of this download instance.

        :param file: the name of the file
        :return: the full path to the file
        """

        return os.path.join(self.path, file)
