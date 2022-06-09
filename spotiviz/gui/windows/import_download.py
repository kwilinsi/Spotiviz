from datetime import datetime
import os.path

from PyQt6.QtCore import Qt, QDateTime, QDate, QRegularExpression
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit,
    QFileDialog, QSizePolicy, QFrame, QGridLayout
)
from PyQt6.QtGui import QRegularExpressionValidator

from spotiviz.projects.structure.project_class import Project

from spotiviz.gui.widgets.labels import Header, Error
from spotiviz.gui.windows.standard_windows import CenteredWindow
from spotiviz.gui.widgets.generic_buttons import PrimaryBtn, SecondaryBtn


class ImportDownload(CenteredWindow):
    """
    This class constitutes the popup window that is shown whenever a user
    imports a new Spotify download into a project. It asks the user for the
    name of the download, the directory it points to, and the date that the
    Download was requested from Spotify.
    """

    def __init__(self, project: Project):
        """
        Create a new ImportDownload popup window. The project that the import
        will go to must be specified in order to add that download.

        Args:
            project: The project to which the Spotify download will be added.
        """

        super().__init__(QVBoxLayout())

        self.project = project

        # Define variables that will be set later
        self.field_path = None
        self.field_name = None
        self.field_date = None
        self.btn_import = None
        self.date_error = None
        self.date = None

        self.setWindowTitle(f'{self.project.name} - Import')

        # Create and populate layouts
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
        fields = QGridLayout()
        buttons_layout = QHBoxLayout()

        # Set spacing
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        # Populate layouts

        # Add the header
        title = Header('Import Spotify Download')
        title.setContentsMargins(0, 0, 0, 10)
        self.layout.addWidget(title)

        # Add layouts to main layout
        self.layout.addLayout(fields)
        self.layout.addLayout(buttons_layout)

        # Add the prompt for the path
        prompt_path = QLabel('Folder:')
        # noinspection PyArgumentList
        self.field_path = QLabel('Select Spotify download folder')
        self.field_path.setProperty('bordered-label', True)
        self.field_path.setSizePolicy(QSizePolicy.Policy.Expanding,
                                      QSizePolicy.Policy.Preferred)
        path_browse_btn = QPushButton('Browse')
        path_browse_btn.clicked.connect(self.update_path)
        fields.addWidget(prompt_path, 0, 0)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.field_path)
        path_layout.addWidget(path_browse_btn)
        fields.addLayout(path_layout, 0, 1)

        # Add the prompt for the name
        prompt_name = QLabel('Name:')
        # noinspection PyArgumentList
        self.field_name = QLineEdit(placeholderText='Enter download name')
        fields.addWidget(prompt_name, 1, 0)
        fields.addWidget(self.field_name, 1, 1)

        # Add the prompt for the date
        prompt_date = QLabel('Date [optional]:')
        # noinspection PyArgumentList
        self.field_date = QLineEdit(
            placeholderText=datetime.now().strftime('%m/%d/%Y'))
        max_width = self.field_date.fontMetrics().horizontalAdvance(
            '06/09/2002') * 2
        self.field_date.setMaximumWidth(max_width)
        validator = QRegularExpressionValidator(
            QRegularExpression('[\\d/-]{0,10}'))
        self.field_date.setValidator(validator)
        self.date_error = Error('')

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.field_date)
        date_layout.addWidget(self.date_error)

        fields.addWidget(prompt_date, 2, 0)
        fields.addLayout(date_layout, 2, 1)

        # Add the cancel and import buttons
        btn_cancel = SecondaryBtn('Cancel')
        btn_cancel.clicked.connect(self.close)
        self.btn_import = PrimaryBtn('Import')
        self.btn_import.clicked.connect(self.on_import_click)
        # Import is initially disabled until a path is chosen
        self.btn_import.setEnabled(False)
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(self.btn_import)
        buttons_layout.setContentsMargins(0, 10, 0, 0)

    def update_path(self) -> None:
        """
        This is called whenever the user clicks the 'Browse' button to select
        the directory containing the Spotify download.

        Returns:
            None
        """

        d = QFileDialog.getExistingDirectory(
            self,
            'Open Spotify Download Directory'
        )

        if d:
            self.field_path.setText(d)
            self.field_name.setText(os.path.basename(d))
            self.btn_import.setEnabled(True)

    def on_import_click(self) -> None:
        """
        This is called when the user clicks the 'Import' button at the bottom
        of the dialog, triggering the import.

        Returns:
            None
        """

        try:
            self.validate_date()
        except ValueError:
            return
        self.date_error.setText('')

        print('Imported')
        self.close()

    def validate_date(self) -> None:
        """
        Make sure the date field is either empty or contains a valid date. If
        it's not valid, an error message is placed next to the date field and
        a ValueError is raised.

        The parsed date is stored in self.date for later.

        Returns:
            None

        Raises:
            ValueError: If the date is not valid.
        """

        date = self.field_date.text()
        self.date = None

        # If there is no date, it passes validation, as it's optional
        if not date:
            return

        # Attempt to parse the date
        formats = ['%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y']
        for f in formats:
            try:
                self.date = datetime.strptime(date, f)
            except ValueError:
                pass

        # If the date wasn't set, the formatting failed
        if self.date is None:
            self.date_error.setText(
                'Invalid date: use format mm/dd/yyyy.')
            raise ValueError()

        if self.date > datetime.now():
            self.date_error.setText(
                'The download can\'t be from the future.')
            raise ValueError()

        if self.date < datetime(2006, 4, 23):
            self.date_error.setText(
                'Date must be after Spotify was founded.')
            raise ValueError
