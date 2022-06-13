from typing import Callable

from PyQt6.QtWidgets import (
    QDialog, QGridLayout, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)

from spotiviz.projects.structure.spotify_download import SpotifyDownload

from spotiviz.gui.widgets.download_button import DownloadBtn
from spotiviz.gui.widgets.generic_buttons import DeleteBtn, SecondaryBtn


class DownloadInfo(QDialog):
    def __init__(self,
                 download: SpotifyDownload,
                 delete_fnc: Callable,
                 download_btn: DownloadBtn,
                 parent):
        """
        Create a new DownloadInfo dialog for a specific Spotify Download.

        Args:
            download: The download shown in this dialog.
            delete_fnc: The function to call if the "Delete" button is clicked.
            parent: The parent window
        """

        super().__init__(parent)

        self.download = download
        self.delete_fnc = delete_fnc
        self.download_btn = download_btn

        self.setWindowTitle(download.name)

        layout = QVBoxLayout()
        inf_layout = QGridLayout()
        btn_layout = QHBoxLayout()
        layout.addLayout(inf_layout)
        layout.addLayout(btn_layout)

        layout.setSpacing(20)
        inf_layout.setSpacing(15)

        self.setLayout(layout)

        # Populate info
        name_lbl = QLabel('Name')
        name_val = QLabel(download.name)
        inf_layout.addWidget(name_lbl, 0, 0)
        inf_layout.addWidget(name_val, 0, 1)

        path_lvl = QLabel('Path')
        path_val = QLabel(download.path)
        inf_layout.addWidget(path_lvl, 1, 0)
        inf_layout.addWidget(path_val, 1, 1)

        date_lvl = QLabel('Date:')
        date_val = QLabel(download.date.strftime('%m/%d/%Y') if download.date
                          else 'N/A')
        inf_layout.addWidget(date_lvl, 2, 0)
        inf_layout.addWidget(date_val, 2, 1)

        # Add buttons
        close_btn = SecondaryBtn('Close')
        close_btn.clicked.connect(self.close)
        delete_btn = DeleteBtn('Delete')
        delete_btn.clicked.connect(self.delete_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(delete_btn)

    def delete_btn(self) -> None:
        """
        This is called when the user clicks the "Delete" button. It closes
        the window and calls the function assigned when the dialog was created.

        Returns:
            None
        """

        self.close()
        self.delete_fnc()
