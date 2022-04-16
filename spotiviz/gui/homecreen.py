from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)

from spotiviz.gui.widgets.header import Header
from spotiviz.gui.widgets.main_button import MainButton
from spotiviz.gui.widgets import db_widgets


class HomeScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spotiviz - Home")

        # Create layouts
        page_layout = QVBoxLayout()
        main_buttons_layout = QHBoxLayout()
        project_list_layout = QVBoxLayout()

        # Define main project buttons
        btn_open = MainButton("Open Project")
        main_buttons_layout.addWidget(btn_open)

        btn_new = MainButton("New Project")
        main_buttons_layout.addWidget(btn_new)

        # Create list of recent projects
        project_list_lbl = Header("Recent Projects")

        project_list_layout.addWidget(project_list_lbl)
        for b in db_widgets.get_all_project_buttons():
            project_list_layout.addWidget(b)

        # Set padding and alignment
        page_layout.setContentsMargins(150, 50, 150, 50)
        page_layout.setSpacing(20)
        project_list_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Combine layouts
        page_layout.addLayout(main_buttons_layout)
        page_layout.addLayout(project_list_layout)

        frame = QFrame()
        frame.setLayout(page_layout)
        self.setCentralWidget(frame)

        self.resize(800, 500)
