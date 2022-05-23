from __future__ import annotations

from spotiviz.projects.structure import (
    project_class as pc, spotify_download as sd
)


class GenericFile:
    """
    This is the super class of all file types in SpotifyDownloads.
    """

    def __init__(self,
                 project: pc.Project,
                 download: sd.SpotifyDownload,
                 file_name: str):
        """
        Create an object representing a file in a Spotify download.

        Args:
            project: The project to which the download (and therefore this
                     file) is attached.
            download: The SpotifyDownload, which points to the folder
                      containing this file.
            file_name: The name of this file within the download folder.
        """

        self.project = project
        self.download = download
        self.file_name = file_name
