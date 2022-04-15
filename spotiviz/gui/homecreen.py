from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, \
    QPushButton, \
    QWidget, QLabel


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
        page_layout.setSpacing(20)

        # Combine layouts
        page_layout.addLayout(main_buttons_layout)
        page_layout.addLayout(project_list_layout)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)
