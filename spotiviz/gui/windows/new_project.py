import os.path
from pathlib import Path
import random

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QLineEdit,
    QFileDialog, QPushButton
)

from spotiviz.projects import utils, manager

from spotiviz.gui.windows.standard_windows import CenteredWindow
from spotiviz.gui.widgets.labels import Header
from spotiviz.gui.widgets.generic_buttons import PrimaryBtn, SecondaryBtn


class NewProject(CenteredWindow):
    def __init__(self, create_fnc):
        """
        Create the window for creating a new project.

        Args:
            create_fnc: The function to call when the user clicks the
            'Create' button and makes a new project. This function should
            accept one parameter: the Project instance that was just created.
        """

        super().__init__(QVBoxLayout())

        self.create_fnc = create_fnc

        self.setWindowTitle('Spotiviz - New Project')

        # This becomes True if the user manually selects a database path
        # using the 'Browse' button.
        self.set_manual_path: bool = False

        # Create and populate layouts
        self.field_name = None
        self.field_path = None
        self.create_layout()

        # Set initial window size
        self.set_fixed_size()
        self.resize(700, 400)

    def create_layout(self) -> None:
        """
        This is called once when the window is created. It creates all the
        widgets and layouts in the window.

        Returns:
            None
        """

        # Create layouts
        field_name_layout = QHBoxLayout()
        field_path_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        # Set spacing
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        # Populate layouts

        # Add the header
        title = Header('Create New Project')
        title.setContentsMargins(0, 0, 0, 10)
        self.layout.addWidget(title)

        # Add layouts to main layout
        self.layout.addLayout(field_name_layout)
        self.layout.addLayout(field_path_layout)
        self.layout.addLayout(buttons_layout)

        # Add the prompt for the project name

        prompt_name = QLabel('Name:')
        # noinspection PyArgumentList
        self.field_name = QLineEdit(placeholderText='Enter the project name')
        self.field_name.setText(f'MyProject{random.randint(10000, 99999)}')
        self.field_name.textChanged.connect(self.on_name_change)
        field_name_layout.addWidget(prompt_name)
        field_name_layout.addWidget(self.field_name)

        # Add the prompt for the database path
        prompt_path = QLabel('Path:')
        self.field_path = QLineEdit(
            manager.determine_new_project_path(self.name()))
        path_browse_btn = QPushButton('Browse')
        path_browse_btn.clicked.connect(self.open_file_browser)
        field_path_layout.addWidget(prompt_path)
        field_path_layout.addWidget(self.field_path)
        field_path_layout.addWidget(path_browse_btn)

        # Add the cancel and create buttons
        btn_cancel = SecondaryBtn('Cancel')
        btn_cancel.clicked.connect(self.close)
        btn_create = PrimaryBtn('Create')
        btn_create.clicked.connect(self.create_project)
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_create)

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

        # If the user has already set the path manually, don't change it
        if self.set_manual_path:
            return

        # Get current directory. Use the parent dir unless the path is
        # already pointing to a directory
        d = self.path()
        d = d if os.path.isdir(d) else Path(d).parent.absolute()

        # Determine the file name
        f = utils.clean_project_name(self.name()) if len(self.name()) else ''

        # Combine directory and file and set as the path
        self.field_path.setText(os.path.join(d, f))

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

        p = manager.create_project(self.name(), self.path())
        self.close()
        self.create_fnc(p)
