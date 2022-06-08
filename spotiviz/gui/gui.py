import os.path

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

from spotiviz.database import db

from spotiviz.gui import constants as const
from spotiviz.gui.windows import homecreen
from spotiviz.utils import resources as resc

APP = None
HOME = None
PROJECT = None


def start() -> None:
    """
    Start the main GUI, initializing the Qt application and displaying the
    home screen.

    This also initializes the global SQLAlchemy database engine.

    Returns:
        None
    """

    global APP, HOME

    db.initialize()

    APP = QApplication([])

    # Load the fonts
    load_fonts()

    # Load the QSS style sheet
    APP.setStyleSheet(resc.read(resc.get_gui_resource(const.QSS_GLOBAL_STYLES)))

    HOME = homecreen.HomeScreen()
    HOME.show()

    APP.exec()


def load_fonts() -> None:
    """
    Load all the fonts in the resources folder into Qt so that they can be
    used in the stylesheets.

    Returns:
        None
    """

    fonts_dir = resc.get_gui_resource(os.path.join('fonts'))

    for root, _, files in os.walk(fonts_dir):
        for f in files:
            QFontDatabase.addApplicationFont(os.path.join(root, f))
