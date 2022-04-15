from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from spotiviz.gui import homecreen

APP = None
HOME = None


def start() -> None:
    """
    Start the main GUI, initializing the Qt application and displaying the
    home screen.

    Returns:
        None
    """

    global APP, HOME

    APP = QApplication([])

    HOME = homecreen.HomeScreen()
    HOME.show()

    APP.exec()
