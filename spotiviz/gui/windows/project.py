from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QFrame, QFileDialog
from PyQt6.QtGui import QAction

from spotiviz.projects.structure.project_class import Project

from spotiviz.gui import gui
from spotiviz.gui.windows.standard_windows import BaseWindow
from spotiviz.gui.widgets.labels import Header, Subtitle
from spotiviz.gui.widgets.generic_buttons import MainBtn


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

        # Create the body layout and add it to the base
        self.body_layout = QVBoxLayout()
        self.base_layout.addLayout(self.body_layout)

        # Define the actions and menu bar
        self.action_import = None
        self.action_close = None
        self.action_close_project = None
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

        self.body_layout.setContentsMargins(50, 50, 50, 50)

        # Add the empty project frame to the body
        self.body_layout.addWidget(self.get_empty_project_layout())

    def get_empty_project_layout(self) -> QFrame:
        """
        Get a frame widget containing the standard widgets for an empty
        project: a header and a button to import Spotify downloads.

        Returns:
            A QFrame containing the widgets.
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
        btn_open.clicked.connect(self.import_download_btn)
        btn_open_layout.addWidget(btn_open)
        layout.addLayout(btn_open_layout)

        frame.setMaximumSize(frame.sizeHint() * 1.25)

        return frame

    def import_download_btn(self) -> None:
        """
        This is called whenever the user requests to import a Spotify
        download. It opens a file dialog for the user to select the directory.

        Returns:
            None
        """

        d = QFileDialog.getExistingDirectory(
            self,
            'Open Spotify Download Directory'
        )

        if d:
            print(f'User imported directory \'{d}\'')

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
