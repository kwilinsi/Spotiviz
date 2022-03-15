import os

from src.cleaner.spotifyDownload import SpotifyDownload
from src.utils.log import LOG

DEFAULT_NAME = 'Unnamed Collection'


class DownloadCollection:
    def __init__(self, path: str = None, name: str = None):
        """
        Create a new download collection instance.

        Optionally, specify the path to some directory. That path will be
        passed to the addSpotifyDownloads() methods, and the contents of
        the directory will be indexed to locate spotify downloads.

        Additionally, a name can optionally be specified for this download
        collection. If a name is not given, it will be set to the name of the
        innermost directory in the path. If neither argument is given,
        the name will be set to the default name and updated only if the
        addSpotifyDownloads method is called.

        :param path: the path to the root directory
        """

        # Initialize the list of downloads
        self.spotifyDownloads = []

        # Set the name
        if name:
            self.name = name
        else:
            self.name = DEFAULT_NAME

        # Add downloads based on the path
        if path:
            self.addSpotifyDownloads(path)

        LOG.info('Initialized Download Collection.')
        LOG.info('  Name = {n}'.format(n=self.name))
        LOG.info('  Path = {p}'.format(p=path))
        LOG.info('  Downloads = {s}'.format(s=len(self.spotifyDownloads)))

    def addSpotifyDownload(self, path: str) -> bool:
        """
        Add a spotify download to this collection by specifying the path to
        the directory with the download.
        :param path: the path to the download
        :return: True if the path is resolved to a valid spotify download;
        False otherwise
        """

        s = SpotifyDownload(path)
        if s.isValidDownload():
            self.spotifyDownloads.append(s)
            return True
        else:
            return False

    def addSpotifyDownloads(self, path: str):
        """
        Given a path to some root directory, walk through all the
        subdirectories looking for valid Spotify data downloads. Add all of
        them to the downloads in this collection instance.

        If the name of this collection is missing or the default name,
        this will also overwrite the name to be the name of the innermost
        directory in the path.

        :param path: the path to the root directory to index
        """

        # If the given path is invalid, exit
        if not os.path.isdir(path):
            return

        # If the collection name hasn't been set yet, set it now
        if not self.name or self.name == DEFAULT_NAME:
            self.name = os.path.basename(path)

        # Add all valid spotify data subdirectories
        for d in [root for (root, dirs, files) in os.walk(path)]:
            s = SpotifyDownload(d)
            if s.isValidDownload():
                self.spotifyDownloads.append(s)

    def loadStreamingHistories(self):
        """
        Iterate through each of the spotify download instances attached to
        this collection. Load each of the streaming history files from each
        download and compile them all into a sqlite database.
        :return:
        """


