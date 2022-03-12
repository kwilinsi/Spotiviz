import enum
import re

STREAMING_REGEX = r'^StreamingHistory\d\.json$'
PLAYLIST_REGEX = r'^Playlist\d\.json$'
IDENTITY_REGEX = r'^Identity\.json$'
LIBRARY_REGEX = r'^YourLibrary\.json$'

class FileType(enum.Enum):
    """
    This class represents the type of a data file from a Spotify download.
    This is based on the name of the file and is assigned via
    """
    UNKNOWN = 0
    STREAMING = 1
    PLAYLIST = 2
    IDENTITY = 3
    LIBRARY = 4


def getFileType(fileName: str) -> FileType:
    """
    Get the type of the given file from a Spotify data download. The file is
    assigned a type based on its name, matched using regex.

    :param fileName: the name of the file (not the full path)
    :return: a filetype enum instance representing the type of the given file
    """

    if re.match(STREAMING_REGEX, fileName):
        return FileType.STREAMING
    elif re.match(PLAYLIST_REGEX, fileName):
        return FileType.PLAYLIST
    elif re.match(IDENTITY_REGEX, fileName):
        return FileType.IDENTITY
    elif re.match(LIBRARY_REGEX, fileName):
        return FileType.LIBRARY
    else:
        return FileType.UNKNOWN
