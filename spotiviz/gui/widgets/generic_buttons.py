from typing import Callable

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QSizePolicy

from spotiviz.gui.icons import Icons


class PrimaryBtn(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)

        self.setMinimumSize(100, 30)
        self.setMaximumSize(125, 30)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Expanding)


class SecondaryBtn(PrimaryBtn):
    def __init__(self, text: str):
        super().__init__(text)


class DeleteBtn(PrimaryBtn):
    def __init__(self, text: str):
        super().__init__(text)


class MainBtn(PrimaryBtn):
    def __init__(self, text: str):
        super().__init__(text)

        self.setMinimumSize(130, 40)
        self.setMaximumSize(175, 40)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Expanding)


class InfoBtn(QPushButton):
    """
    The info button is a small button with the info icon.
    """

    def __init__(self, click_fcn: Callable):
        """
        Create a new info button.

        Args:
            click_fcn: The function to execute when the button is clicked.
        """

        super().__init__()

        self.setIcon(QIcon(Icons.INFO.path()))
        self.clicked.connect(click_fcn)
