from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QLineEdit
)


class NewProject(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Spotiviz - New Project')

        # Create layouts
        page_layout = QVBoxLayout()
        field_name_layout = QHBoxLayout()
        field_path_layout = QHBoxLayout()

        # Populate layouts

        title = QLabel('Create New Project')
        page_layout.addWidget(title)

        page_layout.addLayout(field_name_layout)
        page_layout.addLayout(field_path_layout)

        prompt_name = QLabel('Project name:')
        field_name = QLineEdit()
        field_name_layout.addWidget(prompt_name)
        field_name_layout.addWidget(field_name)

        prompt_path = QLabel('Project path:')
        field_path = QLineEdit()
        field_path_layout.addWidget(prompt_path)
        field_path_layout.addWidget(field_path)

        # Assign everything to the main window
        w = QWidget()
        w.setLayout(page_layout)
        self.setCentralWidget(w)
        self.resize(600, 400)
