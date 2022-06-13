from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QStackedLayout, QScrollArea, QWidget, QSizePolicy
)

from sqlalchemy import select, func, delete
from sqlalchemy.exc import NoResultFound

from spotiviz.database.structure.project_struct import Downloads

from spotiviz.projects.structure.project_class import Project
from spotiviz.projects.structure.spotify_download import SpotifyDownload

from spotiviz.gui import gui
from spotiviz.gui.widgets.download_button import DownloadBtn
from spotiviz.gui.widgets.generic_buttons import MainBtn, PrimaryBtn
from spotiviz.gui.widgets.labels import Header, Subtitle
from spotiviz.gui.widgets.not_implemented import this_is_not_yet_implemented
from spotiviz.gui.windows.download_info import DownloadInfo
from spotiviz.gui.windows.import_download import ImportDownload
from spotiviz.gui.windows.standard_windows import BaseWindow


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
        self.action_clear_downloads = None
        self.action_delete_project = None

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
        self.action_import.triggered.connect(self.btn_import_download)

        self.action_close = QAction('&Close', self)
        self.action_close.triggered.connect(self.close_program)

        self.action_close_project = QAction('Close &Project', self)
        self.action_close_project.triggered.connect(self.close_project)

        self.action_clear_downloads = QAction('Clear all downloads', self)
        self.action_clear_downloads.triggered.connect(self.btn_clear_downloads)

        self.action_delete_project = QAction('Delete project', self)
        self.action_delete_project.triggered.connect(self.btn_delete_project)

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
        file_menu.addSeparator()

        project_submenu = file_menu.addMenu('Project')
        project_submenu.addAction(self.action_clear_downloads)
        project_submenu.addAction(self.action_delete_project)

        edit_menu = menu.addMenu('&Edit')

        edit_menu.addAction(self.action_preferences)

    def btn_spotify_download(self) -> None:
        """
        This is called whenever a user clicks one of the Spotify Download
        buttons in the project body. It opens a window where they can see
        more information on the download and possibly remove it from the
        project.

        Returns:
            None
        """

        sender_btn: DownloadBtn = self.sender()
        dialog = DownloadInfo(sender_btn.download,
                              self.btn_delete_download,
                              sender_btn,
                              self)
        dialog.exec()

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

        gui.load_homescreen()
        gui.HOME.show()
        self.close()

    def btn_import_download(self) -> None:
        """
        This is called whenever the user requests to import a Spotify
        download. It opens the import download popup window.

        Returns:
            None
        """

        self.import_popup = ImportDownload(self.project,
                                           self.btn_add_download)
        self.import_popup.show()

    def btn_add_download(self) -> None:
        """
        This is called when the user clicks "Import" button in an
        ImportDownload window to add a new Spotify download to the project.
        It triggers a refresh of the downloads list and re-enables the 'Load'
        button (if it was disabled) to allow loading the contents of the new
        download.

        Returns:
            None
        """

        self.body_layout.refresh()
        self.body_layout.btn_load.setEnabled(True)

    def btn_delete_download(self) -> None:
        """
        This function is called whenever a user clicks the "Delete" button in
        the DownloadInfo popup dialog for a Spotify download. It removes the
        download and all of its data from the SQLite database and removes the
        download's button in the project window.

        Returns:
            None
        """

        sender: DownloadInfo = self.sender().parent()
        download: SpotifyDownload = sender.download
        with self.project.open_session() as session:
            try:
                stmt = select(Downloads).where(Downloads.id == download.id)
                session.delete(session.scalars(stmt).one())
                session.commit()
            except NoResultFound:
                print('No result found')

        sender.download_btn.setParent(None)
        self.body_layout.refresh()

    def btn_load_downloads(self) -> None:
        """
        This function is called when the user clicks the "Load" button
        beneath the list of downloads. It loads the file contents of each of
        those downloads in to the project database file. Once every download
        is loaded, the button is disabled.

        Returns:
            None
        """

        self.body_layout.btn_load.setDisabled(True)

        # Find all non-loaded downloads and load them
        with self.project.open_session() as session:
            stmt = select(Downloads).where(Downloads.loaded == False)
            result = session.scalars(stmt)
            for r in result:
                SpotifyDownload.from_sql(self.project, r).load()

        self.body_layout.refresh()

    def btn_clear_downloads(self) -> None:
        """
        This function is called when the user chooses the 'Clear all
        downloads' option in the menubar. It removes all the Spotify
        downloads associated with the project and updates the project window
        accordingly.

        Returns:
            None
        """

        with self.project.open_session() as session:
            session.execute(delete(Downloads))
            session.commit()

        self.body_layout.refresh()

    def btn_delete_project(self) -> None:
        """
        This function is called when the user chooses the 'Delete project'
        option in the menubar. It deletes the project's SQLite database and
        removes this project from the program database. Then it calls
        self.close_project() to return to the homescreen.

        Returns:
            None
        """

        self.project.delete()
        self.close_project()


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

        # Define data members to be initialized later
        self.btn_load = None

        self.empty_project = self.get_empty_project()
        self.addWidget(self.empty_project)

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

        downloads = self.project.get_downloads()

        # If there are no downloads, add the empty project layout to this frame
        if not downloads:
            self.setCurrentIndex(0)
            return

        # Otherwise, list the downloads
        self.update_downloads_list(downloads)
        self.setCurrentIndex(1)

    def get_empty_project(self) -> QWidget:
        """
        Create the widget that contains the standard widgets for an empty
        project: a header and a button to import Spotify downloads. Put this
        layout in a frame and center it within a generic widget.

        This frame will be stored in self.empty_project.

        Returns:
            A widget containing the layout.
        """

        # Create frame and layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

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
        btn_open.clicked.connect(self.window.btn_import_download)
        btn_open_layout.addWidget(btn_open)
        layout.addLayout(btn_open_layout)

        widget.setFixedSize(widget.sizeHint())

        # Now enclose the widget in ANOTHER layout inside another frame. This
        # is necessary to be able to center it within self, a StackedLayout.
        enclosing_widget = QWidget()
        enclosing_layout = QVBoxLayout()
        enclosing_widget.setLayout(enclosing_layout)
        enclosing_layout.addWidget(widget)
        enclosing_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return enclosing_widget

    def get_scroll_downloads_list(self) -> QWidget:
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
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Add the header
        head = Header('Spotify Downloads')
        head.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(head)

        self.lyt_downloads_list.addStretch()
        self.lyt_downloads_list.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Add the scrollable layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        list_widget = QWidget()
        list_widget.setLayout(self.lyt_downloads_list)
        scroll.setWidget(list_widget)
        layout.addWidget(scroll)

        # Add the 'Load' and 'Process' buttons
        btn_lyt = QHBoxLayout()
        self.btn_load = PrimaryBtn('Load')
        self.btn_load.clicked.connect(self.window.btn_load_downloads)
        btn_process = PrimaryBtn('Process')
        btn_process.clicked.connect(lambda: this_is_not_yet_implemented(
            self.window))
        btn_lyt.addWidget(self.btn_load)
        btn_lyt.addWidget(btn_process)
        btn_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_lyt.setContentsMargins(0, 10, 10, 0)
        layout.addLayout(btn_lyt)

        # Determine if there's any un-loaded projects. If there aren't any,
        # disable the 'Load' button
        with self.project.open_session() as session:
            stmt = select(func.count(Downloads.loaded)).where(
                Downloads.loaded == False)
            count = session.scalars(stmt).one()
            if not count:
                self.btn_load.setDisabled(True)

        # Set sizing
        widget.setMinimumWidth(600)
        widget.setMaximumWidth(700)
        widget.setMinimumHeight(250)

        # Now enclose the widget in ANOTHER layout inside another frame. This
        # is necessary to be able to center it within self, a StackedLayout.
        enclosing_widget = QWidget()
        enclosing_layout = QVBoxLayout()
        enclosing_widget.setLayout(enclosing_layout)
        enclosing_layout.addWidget(widget)
        enclosing_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter |
                                      Qt.AlignmentFlag.AlignTop)
        return enclosing_widget

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
            btn, DownloadBtn(downloads[dwn], self.window.btn_spotify_download)
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
