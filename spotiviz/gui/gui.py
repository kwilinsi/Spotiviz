from PyQt6.QtWidgets import QApplication

from spotiviz.gui import homecreen, constants as const
from spotiviz.utils import resources as resc

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
    APP.setStyleSheet(resc.read(resc.get_gui_resource(const.QSS_GLOBAL_STYLES)))

    HOME = homecreen.HomeScreen()
    HOME.show()

    APP.exec()
