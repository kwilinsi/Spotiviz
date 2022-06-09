from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QFileDialog, QLabel
)
from PyQt6.QtGui import QAction

from spotiviz.projects.structure.project_class import Project
from spotiviz.projects.structure.spotify_download import SpotifyDownload

from spotiviz.gui import gui
from spotiviz.gui.windows.import_download import ImportDownload
from spotiviz.gui.windows.standard_windows import BaseWindow
from spotiviz.gui.widgets.labels import Header, Subtitle
from spotiviz.gui.widgets.generic_buttons import MainBtn
from spotiviz.gui.widgets.download_button import DownloadBtn


class ProjectWindow(BaseWindow):
    def __init__(self,
                 project: Project):
        """
        Create a ProjectWindow for a specified Spotiviz project.

        Args:
            project: The project controlled by this window.
        """

        super().__init__(QVBoxLayout())

        # Attach the project instance to this window
        self.project = project

        # Declare variables that will be defined elsewhere
        self.import_popup = None
        self.action_import = None
        self.action_close = None
        self.action_close_project = None

        # --------------------

        # Create the body layout and add it to the base
        self.body_layout = QVBoxLayout()
        self.base_layout.addLayout(self.body_layout)

        # Define the actions and menu bar
        self.define_actions()
        self.create_menubar()

        self.create_layout()

        self.setWindowTitle(self.project.name)

    def define_actions(self) -> None:
        """
        Define the actions that are found in the menu bar of the window. This
        is called once when the window is created, just before calling
        .create_menubar().

        Returns:
            None
        """

        self.action_import = QAction('&Import', self)
        self.action_import.setToolTip('Import a Spotify Download')
        self.action_import.triggered.connect(self.import_download_btn)

        self.action_close = QAction('&Close', self)
        self.action_close.triggered.connect(self.close_program)

        self.action_close_project = QAction('Close &Project', self)
        self.action_close_project.triggered.connect(self.close_project)

    def create_menubar(self) -> None:
        """
        This is called once when the window is created to define the menu bar
        at the top. It is called after .define_actions(), as it depends on
        those actions to function.

        Returns:
            None
        """

        menu = self.menuBar()
        file_menu = menu.addMenu('&File')

        file_menu.addAction(self.action_import)
        file_menu.addSeparator()
        file_menu.addAction(self.action_close)
        file_menu.addAction(self.action_close_project)

    def create_layout(self) -> None:
        """
        This is called once when the window is created. It creates all the
        widgets and layouts in the window.

        Returns:
            None
        """

        self.body_layout.setContentsMargins(50, 50, 50, 50)
        self.fill_body_layout()

    def fill_body_layout(self) -> None:
        """
        The body layout changes often as the project is manipulated. This
        reloads the body layout every time it needs to be modified.
        Initially, this sets the body layout to the standard empty project
        layout.

        Returns:
            None
        """

        downloads = self.project.get_downloads()

        # If there are no downloads, add the empty project frame to the body
        if not downloads:
            l = self.get_empty_project_layout()
            if self.body_layout.itemAt(0):
                self.body_layout.itemAt(0).deleteLater()
            self.body_layout.addWidget(l)
            return

        # Otherwise, list the downloads in the body
        l = self.get_downloads_layout(downloads)
        if self.body_layout.itemAt(0):
            self.body_layout.itemAt(0).deleteLater()
        self.body_layout.addWidget(l)

    def get_empty_project_layout(self) -> QFrame:
        """
        Get a frame widget containing the standard widgets for an empty
        project: a header and a button to import Spotify downloads.

        Returns:
            A QFrame containing the widgets.
        """

        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create frame and layout
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # Set spacing and alignment
        layout.setSpacing(10)

        # Add text
        head = Header('There\'s nothing here')
        sub = Subtitle('Import a Spotify download to get started.')
        layout.addWidget(head)
        layout.addWidget(sub)

        # Add open button
        btn_open_layout = QVBoxLayout()
        btn_open_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_open = MainBtn('Import')
        btn_open.clicked.connect(self.import_download_btn)
        btn_open_layout.addWidget(btn_open)
        layout.addLayout(btn_open_layout)

        frame.setMaximumSize(frame.sizeHint())

        return frame

    def get_downloads_layout(self, downloads: List[SpotifyDownload]) -> QFrame:
        """
        Create a layout for the body of the project window that lists all the
        Spotify downloads associated with the project.

        Args:
            downloads: The list of downloads.

        Returns:
            The layout embedded in a QFrame widget.
        """

        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create frame and layout
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # Add text
        head = Header('Spotify Downloads')
        head.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(head)

        # Add buttons for each Spotify download
        for download in downloads:
            layout.addWidget(
                DownloadBtn(download, self.spotify_download_btn))

        layout.setSpacing(10)

        return frame

    def spotify_download_btn(self) -> None:
        """
        This is called whenever a user clicks one of the Spotify Download
        buttons in the project body. It opens a window where they can see
        more information on the download and possibly remove it from the
        project.

        Returns:
            None
        """

        print('Clicked spotify download button')

    def import_download_btn(self) -> None:
        """
        This is called whenever the user requests to import a Spotify
        download. It opens the import download popup window.

        Returns:
            None
        """

        self.import_popup = ImportDownload(self.project)
        self.import_popup.show()

    def close_program(self) -> None:
        """
        This is called when a user clicks the 'Close' button in the 'File'
        menu. It closes the program.

        Returns:
            None
        """

        self.close()

    def close_project(self) -> None:
        """
        This is called when a user clicks the 'Close Project' button in the
        'File' menu. It closes this window, but first it creates a new GUI
        window for the homepage, allowing the user to open a different
        project or create a new one.

        Returns:
            None
        """

        gui.HOME.show()
        self.close()
