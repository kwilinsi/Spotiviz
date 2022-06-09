from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QSizePolicy

from spotiviz.projects.structure.spotify_download import SpotifyDownload


class DownloadBtn(QPushButton):
    """
    This is a button that represents a Spotify download. It appears in the
    main project window to show the downloads currently associated with a
    project.
    """

    def __init__(self,
                 download: SpotifyDownload,
                 click_fcn: Callable):
        """
        Create a new DownloadBtn by providing a SpotifyDownload that it
        represents.

        Args:
            download: The download represented by this button.
            click_fcn: The function to call when this button is clicked.
        """

        super().__init__()

        self.download = download

        layout = QHBoxLayout()

        # Get the download name, path, and date as labels
        name_lbl = QLabel(download.name)
        path_lbl = QLabel(download.path)
        date_lbl = QLabel(download.date.strftime('%m/%d/%Y')
                          if download.date else 'N/A')

        date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight |
                              Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(name_lbl)
        layout.addWidget(path_lbl)
        layout.addWidget(date_lbl)

        layout.setSpacing(30)
        self.setLayout(layout)
        self.setMinimumSize(400, 50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Preferred)

        # Set the function to call when clicked
        self.clicked.connect(click_fcn)
