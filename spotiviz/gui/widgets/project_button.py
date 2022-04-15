import os.path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QSizePolicy


class ProjectButton(QPushButton):
    """
    This is a button that represents a "recent project". It contains the
    project name and the path to that project's database file.
    """

    def __init__(self, project: str, path: str = None):
        """
        Create a new ProjectButton.

        If the path is None, the button will be disabled and the path will be
        replaced with a message indicating that the project isn't valid.

        If the path is provided but doesn't point to a valid file, it will be
        displayed in red and the button will be disabled.

        Args:
            project: The name of the project.
            path: The location of the project's SQLite database file.
        """

        super().__init__()

        layout = QHBoxLayout()

        # Get the project name and path as labels
        name_lbl = QLabel(project)
        if path is not None and os.path.isfile(path):
            path_lbl = QLabel(path)
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
        self.setMaximumSize(500, 75)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
