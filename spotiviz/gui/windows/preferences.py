from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QFormLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QDialogButtonBox, QMainWindow, QWidget,
    QLayout, QScrollArea, QMessageBox
)

from sqlalchemy import update

from spotiviz.database.structure.project_struct import Config as ConfigTbl

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
        self.fields: List[ConfigField] = []

        self.setWindowTitle('Preferences')

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
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.clicked.connect(self.btn_clicked)
        layout.addWidget(self.buttons)

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

        # Forcibly reload the project config from the database
        self.project.config.read_from_db()

        # Add form entries
        for prop in self.project.config.properties:
            self.fields.append(ConfigField(prop, self, self.project))
            form.addRow(QLabel(prop.value.friendly_name), self.fields[-1])

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

    def btn_clicked(self, btn) -> None:
        """
        This function is called when the user clicks either one of the
        buttons at the bottom of the dialog: 'Apply', 'Ok', or 'Cancel'.

        Returns:
            None
        """

        role = self.buttons.buttonRole(btn)

        if role == QDialogButtonBox.ButtonRole.AcceptRole or \
                role == QDialogButtonBox.ButtonRole.ApplyRole:

            # Identify the fields that changed
            changed = [f for f in self.fields if f.has_changed]

            # If any fields changed, update them
            if changed:
                with self.project.open_session() as session:
                    for field in changed:
                        session.execute(
                            update(ConfigTbl).
                                where(ConfigTbl.key == field.config.name).
                                values(value=field.current_value)
                        )
                        field.on_apply()
                    session.commit()

                # Forcibly reload the project config from the database
                self.project.config.read_from_db()

        # If 'Ok' or 'Cancel' were clicked, close the dialog
        if role == QDialogButtonBox.ButtonRole.AcceptRole or \
                role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()


class ConfigField(QHBoxLayout):
    """
    This class represents each of the fields found in the configuration
    section of the preferences dialog. Fields are typically a QLineEdit
    widget,
    but for different data types they may be different widgets.

    Next to each field is also a button that provides more information on
    the
    meaning of the property.
    """

    def __init__(self,
                 config: Config,
                 preferences_dialog: Preferences,
                 project: Project):
        """
        Create a new field by providing the config property that it
        represents.

        Args:
            config: The config property.
            preferences_dialog: The preferences dialog instance to which
            this
                                field belongs.
            project: The project the user is working on.
        """

        super().__init__()

        self.config: Config = config
        self.preferences_dialog: Preferences = preferences_dialog

        self.has_changed: bool = False
        self.initial_value = project.config.properties[config]
        self.current_value = self.initial_value

        # Create input field
        self.field = QLineEdit()
        self.field.textEdited.connect(self.edited)
        self.addWidget(self.field)

        # Set the current value
        self.field.setText(str(self.initial_value))

        # Create an info button
        info_btn = InfoBtn(lambda: self.info_btn(config))
        self.addWidget(info_btn)

    def info_btn(self, config: Config) -> None:
        """
        This function is called when a user clicks one of the info buttons
        next to a config property. It opens a small message box with
        detailed
        information on what the property controls.

        Args:
            config: The config property about which to show information.

        Returns:
            None
        """

        msg = QMessageBox(self.preferences_dialog)
        msg.setWindowTitle(f'{config.value.friendly_name} - Info')
        msg.setText(config.value.description)
        msg.exec()

    def edited(self) -> None:
        """
        This is called whenever the user changes the value in this field. It
        checks to see if the new value is different from the starting value,
        and if so, it updates self.has_changed.

        Returns:
            None
        """

        self.current_value = self.field.text()
        self.has_changed = self.current_value != self.initial_value

    def on_apply(self) -> None:
        """
        This function is called when the user clicks the 'Apply' or 'Ok'
        buttons. Since self.current_value has now been pushed to the
        database, self.initial_value is reset to that value.

        Returns:
            None
        """

        self.initial_value = self.current_value
        self.has_changed = False


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
