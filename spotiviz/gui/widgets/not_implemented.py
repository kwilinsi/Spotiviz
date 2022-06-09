from PyQt6.QtWidgets import QMessageBox, QDialogButtonBox, QVBoxLayout, QLabel


def this_is_not_yet_implemented(parent=None):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle('Nope')
    dialog.setText('This feature is not yet implemented. Sorry.')

    dialog.exec()

