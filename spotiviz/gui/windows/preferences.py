from typing import Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QFormLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QDialogButtonBox, QMainWindow, QWidget,
    QLayout, QScrollArea, QMessageBox
)

from spotiviz.projects.structure.project_class import Project
from spotiviz.projects.structure.config.properties import Config

from spotiviz.gui.widgets.labels import Header
from spotiviz.gui.widgets.generic_buttons import InfoBtn


class Preferences(QDialog):
    """
    This dialog allows the user to change the configuration for the current
    project.
    """

    def __init__(self,
                 parent: QMainWindow,
                 project: Project):
        """
        Create a new preferences dialog associated with a certain project.

        Args:
            parent: The project window on which this dialog should appear.
            project: The project being worked on.
        """

        super().__init__(parent)

        self.project = project

        # Create basic tab layout
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        self.setLayout(layout)

        # Add tabs
        self.config = make_scrollable(self._get_config_tab())
        self.tabs.addTab(self.config, 'Config')
        self.aliases = make_scrollable(self._get_aliases_tab())
        self.tabs.addTab(self.aliases, 'Aliases')

        # Add buttons to this dialog
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _get_config_tab(self) -> QWidget:
        """
        Create the layout for the configuration tab of the dialog.

        Returns:
            The layout.
        """

        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add header
        head = Header('Configuration')
        layout.addWidget(head)

        # Create form layout
        form = QFormLayout()
        layout.addLayout(form)

        # Add form entries
        for prop in self.project.config.properties:
            lbl, h_lyt = self.get_form_property(prop)
            form.addRow(lbl, h_lyt)

        return layout

    def _get_aliases_tab(self) -> QWidget:
        """
        Create the layout for the aliases tab of the dialog.

        Returns:
            The layout.
        """

        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add header
        head = Header('Aliases')
        layout.addWidget(head)

        # Add contents
        lbl = QLabel('This is not yet implemented.')
        layout.addWidget(lbl)

        return layout

    def get_form_property(self, config: Config) -> Tuple[QLabel, QHBoxLayout]:
        """
        Take some configurable property and construct a label and layout for it
        that can be added to the configuration form layout.

        Args:
            config: The configurable property to add to the form.

        Returns:
            A label for the property, and a layout containing a field and
            button
            for getting more info on the button.
        """

        # Create label
        lbl = QLabel(config.value.friendly_name)

        # Create input field
        h_lyt = QHBoxLayout()
        field = QLineEdit()
        h_lyt.addWidget(field)

        # Set the current value
        field.setText(str(self.project.config.properties[config]))

        # Create an info button
        info_btn = InfoBtn(lambda: self.info_btn(config))
        h_lyt.addWidget(info_btn)

        return lbl, h_lyt

    def info_btn(self, config: Config) -> None:
        """
        This function is called when a user clicks one of the info buttons
        next to a config property. It opens a small message box with detailed
        information on what the property controls.

        Args:
            config: The config property about which to show information.

        Returns:
            None
        """

        msg = QMessageBox(self)
        msg.setWindowTitle(f'{config.value.friendly_name} - Info')
        msg.setText(config.value.description)
        msg.exec()


def make_scrollable(layout: QLayout) -> QScrollArea:
    """
    Take a given layout and enclose it in a QScrollArea widget to make it
    scrollable.

    Args:
        layout: The layout to enclose.

    Returns:
        The layout enclosed in a QScrollArea.
    """

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)

    widget = QWidget()
    widget.setLayout(layout)
    scroll.setWidget(widget)

    return scroll
