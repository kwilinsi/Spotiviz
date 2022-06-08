from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget
)

from spotiviz.gui.windows.centered_window import CenteredWindow
from spotiviz.gui.windows.new_project import NewProject
from spotiviz.gui.widgets.header import Header
from spotiviz.gui.widgets.generic_buttons import MainBtn
from spotiviz.gui.widgets import db_widgets


class HomeScreen(CenteredWindow):
    def __init__(self):
        super().__init__(QVBoxLayout())

        self.POPUP = None
        self.POPUP = NewProject()
        self.setWindowTitle('Spotiviz - Home')

        # Populate the window layout
        self.create_layout()

        self.set_fixed_size()
        self.resize(800, 500)

    def create_layout(self) -> None:
        """
        This should be called once when the window is created. It creates all
        the widgets in the window.

        Returns:
            None
        """

        # Create layouts
        main_buttons_layout = QHBoxLayout()
        project_list_layout = QVBoxLayout()

        # Define main project buttons
        btn_new = MainBtn('New Project')
        btn_new.clicked.connect(self.new_project)
        main_buttons_layout.addWidget(btn_new)

        btn_open = MainBtn('Open Project')
        main_buttons_layout.addWidget(btn_open)

        # Create list of recent projects
        project_list_lbl = Header('Recent Projects')

        project_list_layout.addWidget(project_list_lbl)
        proj_buttons = db_widgets.get_all_project_buttons()
        for b in proj_buttons:
            project_list_layout.addWidget(b)

        if len(proj_buttons) == 0:
            no_projects = QLabel('No recent projects found. '
                                 'Create or import one first.')
            no_projects.setProperty('noProjects', True)
            project_list_layout.addWidget(no_projects)

        # Set padding and alignment
        self.layout.setContentsMargins(150, 50, 150, 50)
        self.layout.setSpacing(20)
        main_buttons_layout.setContentsMargins(0, 0, 0, 30)
        project_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop |
                                         Qt.AlignmentFlag.AlignHCenter)

        # Combine layouts
        self.layout.addLayout(main_buttons_layout)
        self.layout.addLayout(project_list_layout)

    def new_project(self, s) -> None:
        """
        Call this when the user creates a new project. It opens a popup
        window for creating the project.

        Returns:
            None
        """

        self.POPUP = NewProject()
        self.POPUP.show()
