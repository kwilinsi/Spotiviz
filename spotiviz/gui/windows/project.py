from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QVBoxLayout, QStackedLayout, QFrame, QScrollArea, QWidget
)

from spotiviz.gui import gui
from spotiviz.gui.widgets.download_button import DownloadBtn
from spotiviz.gui.widgets.generic_buttons import MainBtn
from spotiviz.gui.widgets.labels import Header, Subtitle
from spotiviz.gui.widgets.not_implemented import this_is_not_yet_implemented
from spotiviz.gui.windows.download_info import DownloadInfo
from spotiviz.gui.windows.import_download import ImportDownload
from spotiviz.gui.windows.standard_windows import BaseWindow
from spotiviz.projects.structure.project_class import Project
from spotiviz.projects.structure.spotify_download import SpotifyDownload


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
        self.action_preferences = None

        # --------------------

        # Create the body layout and add it to the base
        self.body_layout = ProjectBody(self)
        self.base_layout.addLayout(self.body_layout)

        # Define the actions and menu bar
        self.define_actions()
        self.create_menubar()

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

        self.action_preferences = QAction('&Preferences', self)
        self.action_preferences.triggered.connect(
            lambda: this_is_not_yet_implemented(self))

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

        edit_menu = menu.addMenu('&Edit')

        edit_menu.addAction(self.action_preferences)

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
        sender_btn = self.sender()
        dialog = DownloadInfo(sender_btn.download,
                              lambda: this_is_not_yet_implemented(self),
                              self)
        dialog.exec()

    def import_download_btn(self) -> None:
        """
        This is called whenever the user requests to import a Spotify
        download. It opens the import download popup window.

        Returns:
            None
        """

        self.import_popup = ImportDownload(self.project,
                                           self.body_layout.refresh)
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


class ProjectBody(QStackedLayout):
    """
    This layout contains the basic contents in the body of the project window.
    It has multiple different views depending on what is being shown.
    """

    def __init__(self, window: ProjectWindow):
        """
        Create the ProjectBody layout by specifying the project window to which
        it is attached.

        Args:
            window: The parent project window to which this is attached,
                    and which contains the actual project data that is shown
                    in the body.
        """

        super().__init__(window)

        self.project = window.project
        self.window = window

        self.frm_empty_project = self.get_frm_empty_project()
        self.addWidget(self.frm_empty_project)

        self.lyt_downloads_list = QVBoxLayout()
        self.addWidget(self.get_scroll_downloads_list())

        self.setContentsMargins(50, 50, 50, 50)

        self.refresh()

    def refresh(self) -> None:
        """
        Set the contents of this frame according to what should be shown in
        the project window (namely some Spotify Downloads or a button to
        import them).

        Returns:
            None
        """

        print('Refreshing body frame...')

        downloads = self.project.get_downloads()

        # If there are no downloads, add the empty project layout to this frame
        if not downloads:
            self.setCurrentIndex(0)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return

        # Otherwise, list the downloads
        self.update_downloads_list(downloads)
        self.setCurrentIndex(1)
        self.setAlignment(Qt.AlignmentFlag.AlignTop |
                          Qt.AlignmentFlag.AlignHCenter)

    def get_frm_empty_project(self) -> QFrame:
        """
        Create the frame that contains the standard widgets for an empty
        project: a header and a button to import Spotify downloads. Put this
        layout in a frame and return it.

        This frame will be stored in self.frm_empty_project.

        Returns:
            A frame containing the layout.
        """

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
        btn_open.clicked.connect(self.window.import_download_btn)
        btn_open_layout.addWidget(btn_open)
        layout.addLayout(btn_open_layout)

        frame.setMaximumSize(frame.sizeHint())

        return frame

    def get_scroll_downloads_list(self) -> QFrame:
        """
        Create the frame for the body of the project window that lists all
        the Spotify downloads associated with the project. This contains the
        layout with the download buttons, self.lyt_downloads_list.

        This frame widget is then added to the second index in the main
        stacked layout.

        Returns:
            A frame containing the layout and scrollable list.
        """

        # Create the main layout and frame
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # Add the header
        head = Header('Spotify Downloads')
        head.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(head)

        self.lyt_downloads_list.addStretch()

        # Add the scrollable layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        widget.setLayout(self.lyt_downloads_list)
        scroll.setWidget(widget)
        layout.addWidget(scroll)

        # scroll.setVerticalScrollBarPolicy(
        # Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        frame.setMinimumWidth(600)

        return frame

    def update_downloads_list(self,
                              downloads: List[SpotifyDownload]) -> None:
        """
        Update the downloads list layout to add each of the current downloads
        as a separate button.

        This updates self.lyt_downloads_list directly.

        Args:
            downloads: The list of downloads associated with this project.

        Returns:
            None
        """

        # Go through each of the old buttons and compare them with the new
        # list of downloads

        btn_index = 0
        dwn_index = 0

        remove_btn = lambda index: self.lyt_downloads_list.removeItem(
            self.lyt_downloads_list.itemAt(index)
        )
        add_btn = lambda btn, dwn: self.lyt_downloads_list.insertWidget(
            btn, DownloadBtn(downloads[dwn], self.window.spotify_download_btn)
        )

        while btn_index < self.lyt_downloads_list.count() - 1 or \
                dwn_index < len(downloads):

            # If there are more downloads and no buttons left, just add the
            # downloads as new buttons
            if btn_index == self.lyt_downloads_list.count() - 1:
                add_btn(self.lyt_downloads_list.count() - 1, dwn_index)
                btn_index += 1
                dwn_index += 1
                continue

            # If there are more buttons and no downloads, remove them
            if dwn_index == len(downloads):
                remove_btn(btn_index)
                continue

            path = self.lyt_downloads_list.itemAt(
                btn_index).widget().download.path

            # If this button isn't in the downloads list anywhere, remove it.
            if path not in [d.path for d in downloads]:
                remove_btn(btn_index)
                continue

            # If this is a new download, add it here
            if path != downloads[dwn_index].path:
                add_btn(btn_index, dwn_index)
            else:
                btn_index += 1

            dwn_index += 1
