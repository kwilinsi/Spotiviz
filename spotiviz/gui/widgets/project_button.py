from typing import Callable

import os.path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QSizePolicy


class ProjectBtn(QPushButton):
    """
    This is a button that represents a "recent project". It contains the
    project name and the path to that project's database file.
    """

    def __init__(self,
                 project: str,
                 path: str = None,
                 click_fcn: Callable = None):
        """
        Create a new ProjectButton.

        If the path is None, the button will be disabled and the path will be
        replaced with a message indicating that the project isn't valid.

        If the path is provided but doesn't point to a valid file, it will be
        displayed in red and the button will be disabled.

        Args:
            project: The name of the project.
            path: The location of the project's SQLite database file.
            click_fcn: The function to call when this button is clicked.
        """

        super().__init__()

        self.project = project

        layout = QHBoxLayout()

        # Get the project name and path as labels
        name_lbl = QLabel(project)
        if path is not None and os.path.isfile(path):
            path_lbl = QLabel(path)
            path_lbl.setProperty('invalidPath', False)
        else:
            path_lbl = QLabel(path) if path is None else QLabel(
                'Missing Database File')
            path_lbl.setProperty('invalidPath', True)
            self.setDisabled(True)

        # Set alignment
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft |
                              Qt.AlignmentFlag.AlignVCenter)
        path_lbl.setAlignment(Qt.AlignmentFlag.AlignRight |
                              Qt.AlignmentFlag.AlignVCenter)

        layout.setSpacing(30)
        layout.addWidget(name_lbl)
        layout.addWidget(path_lbl)

        self.setLayout(layout)
        self.setMinimumSize(400, 50)
        self.setMaximumSize(750, 65)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        # Set the function to call when clicked
        self.clicked.connect(click_fcn)
