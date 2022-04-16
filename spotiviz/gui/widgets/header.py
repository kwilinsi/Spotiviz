from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class Header(QLabel):
    def __init__(self, text: str):
        super().__init__(text)

        self.setAlignment(Qt.AlignmentFlag.AlignHCenter |
                          Qt.AlignmentFlag.AlignBottom)
