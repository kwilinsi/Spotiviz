import os.path
from pathlib import Path
import random

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QLineEdit,
    QFileDialog, QPushButton
)

from spotiviz.projects import utils, manager

from spotiviz.gui.widgets.generic_buttons import PrimaryBtn, SecondaryBtn


class NewProject(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Spotiviz - New Project')

        self.set_manual_path: bool = False

        # Create layouts
        page_layout = QVBoxLayout()
        field_name_layout = QHBoxLayout()
        field_path_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        # Populate layouts

        title = QLabel('Create New Project')
        page_layout.addWidget(title)

        page_layout.addLayout(field_name_layout)
        page_layout.addLayout(field_path_layout)
        page_layout.addLayout(buttons_layout)

        prompt_name = QLabel('Name:')
        self.field_name = QLineEdit(f'MyProject{random.randint(10000, 99999)}')
        self.field_name.textChanged.connect(self.on_name_change)
        field_name_layout.addWidget(prompt_name)
        field_name_layout.addWidget(self.field_name)

        prompt_path = QLabel('Path:')
        self.field_path = QLineEdit(
            manager.determine_new_project_path(self.name()))
        path_browse_btn = QPushButton('Browse')
        path_browse_btn.clicked.connect(self.open_file_browser)
        field_path_layout.addWidget(prompt_path)
        field_path_layout.addWidget(self.field_path)
        field_path_layout.addWidget(path_browse_btn)

        btn_cancel = SecondaryBtn('Cancel')
        btn_cancel.clicked.connect(self.close)
        btn_create = PrimaryBtn('Create')
        btn_create.clicked.connect(self.create_project)
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_create)

        # Assign everything to the main window
        w = QWidget()
        w.setLayout(page_layout)
        self.setCentralWidget(w)
        self.resize(600, 400)

    def open_file_browser(self) -> None:
        """
        Open the file browser to select a path for the project database file.

        Returns:
            None
        """

        path, _ = QFileDialog.getSaveFileName(
            self,
            f'Select Path for {self.name()}',
            utils.clean_project_name(self.name()),
            'Database file (*.db)'
        )

        if path:
            self.field_path.setText(path)
            # Record that the user has now set a manual path, and it
            # shouldn't be automatically updated
            self.set_manual_path = True

    def on_name_change(self) -> None:
        """
        Whenever the project name is changed, the path updates automatically
        UNLESS it has already been set manually by the user.

        Returns:
            None
        """

        if self.set_manual_path:
            return

        # Get current directory
        d = Path(self.path()).parent.absolute()

        self.field_path.setText(
            os.path.join(d, utils.clean_project_name(self.name())))

    def name(self) -> str:
        """
        Retrieve the current name of the project.

        Returns:
            The project name
        """

        return self.field_name.text()

    def path(self) -> str:
        """
        Retrieve the currently selected path to the database.

        Returns:
            The path
        """

        return self.field_path.text()

    def create_project(self) -> None:
        """
        Call this when the 'Create' button is clicked to create a new project.

        Returns:
            None
        """

        manager.create_project(self.name(), self.path())
        self.close()
