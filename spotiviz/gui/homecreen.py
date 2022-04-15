import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QSizePolicy
)

from spotiviz import get_data
from spotiviz.projects import checks, utils


class HomeScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spotiviz - Home")

        # Create layouts
        page_layout = QVBoxLayout()
        main_buttons_layout = QHBoxLayout()
        project_list_layout = QVBoxLayout()

        # Define buttons
        btn_open = QPushButton("Open Project")
        main_buttons_layout.addWidget(btn_open)

        btn_new = QPushButton("New Project")
        main_buttons_layout.addWidget(btn_new)

        # Create project list
        project_list_lbl = QLabel("Recent Projects")
        project_list_lbl.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        btn_proj1 = QPushButton("Project 1")
        btn_proj2 = QPushButton("Project 2")
        btn_proj3 = QPushButton("Project 3")
        project_list_layout.addWidget(project_list_lbl)
        project_list_layout.addWidget(btn_proj1)
        project_list_layout.addWidget(btn_proj2)
        project_list_layout.addWidget(btn_proj3)

        # Set padding
        page_layout.setContentsMargins(200, 50, 200, 50)
        page_layout.setSpacing(20)

        # Combine layouts
        page_layout.addLayout(main_buttons_layout)
        page_layout.addLayout(project_list_layout)

        frame = QFrame()
        frame.setLayout(page_layout)
        self.setCentralWidget(frame)

        self.resize(1000, 621)

    def make_project_button(self, project: str) -> QPushButton:
        """
        Create a button that represents a "recent project". It contains the
        project name and the path to that project's database file.

        If the given project name is invalid, the button will be disabled and
        the path will be replaced with a message indicating that it isn't valid.

        Args:
            project: The name of the project.

        Returns:
            A button for that project.
        """

        # Check to see if the project is valid
        does_exist = checks.does_project_exist(project)

        button = QPushButton()
        layout = QHBoxLayout()

        name_lbl = QLabel(project)
        if does_exist:
            path_lbl = QLabel(get_data(os.path.join(
                'sqlite', 'projects', utils.clean_project_name(project))))
        else:
            path_lbl = QLabel('Missing Database File')

        layout.addWidget(name_lbl)
        layout.addWidget(path_lbl)

        button.setLayout(layout)
        button.setSizePolicy(QSizePolicy.Policy.Preferred,
                             QSizePolicy.Policy.Expanding)

        return button
