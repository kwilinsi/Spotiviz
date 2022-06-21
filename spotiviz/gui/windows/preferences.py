from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QFormLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QDialogButtonBox, QMainWindow, QWidget,
    QLayout, QScrollArea, QMessageBox, QGridLayout, QListWidget,
    QListWidgetItem, QAbstractItemView
)

from sqlalchemy import update, delete, select

from spotiviz.database.structure.project_struct import (
    Aliases, Config as ConfigTbl
)

from spotiviz.projects.structure.project_class import Project
from spotiviz.projects.structure.config.properties import Config

from spotiviz.gui.widgets.labels import Header
from spotiviz.gui.widgets.generic_buttons import InfoBtn, CancelBtn


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
        self.alias_list: AliasList = None

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
        self.aliases = self._get_aliases_tab()
        self.tabs.addTab(self.aliases, 'Aliases')

        # Add buttons to this dialog
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.clicked.connect(self.btn_clicked)
        layout.addWidget(self.buttons)

        # Set initial width wider to accommodate the aliases tab
        self.resize(self.aliases.sizeHint().width() + 75,
                    self.sizeHint().height())

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
        Create the layout/widget for the aliases tab of the dialog.

        Returns:
            The layout.
        """

        # Create layout and enclosing widget
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add header
        head = Header('Aliases')
        layout.addWidget(head)

        # Add contents
        self.alias_list = AliasList(self.project)
        layout.addWidget(self.alias_list)

        # Add buttons
        btn_lyt = QHBoxLayout()
        add_track = QPushButton('Add Track')
        add_track.clicked.connect(lambda: self.alias_list.new_entry(True))
        add_artist = QPushButton('Add Artist')
        add_artist.clicked.connect(lambda: self.alias_list.new_entry(False))
        btn_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_lyt.addWidget(add_track)
        btn_lyt.addWidget(add_artist)
        layout.addLayout(btn_lyt)

        return widget

    def btn_clicked(self, btn) -> None:
        """
        This function is called when the user clicks either one of the
        buttons at the bottom of the dialog: 'Apply', 'Ok', or 'Cancel'.

        Returns:
            None
        """

        role = self.buttons.buttonRole(btn)

        # If 'Apply' or 'Ok' were clicked, apply any changes
        if role == QDialogButtonBox.ButtonRole.AcceptRole or \
                role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.apply_changes()

        # If 'Ok' or 'Cancel' were clicked, close the dialog
        if role == QDialogButtonBox.ButtonRole.AcceptRole or \
                role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()

    def apply_changes(self) -> None:
        """
        This function is called whenever the user clicks the 'Apply' or 'Ok'
        buttons in the dialog. It looks for any changes the user made and
        saves them to the database.

        Returns:
            None
        """

        # Find any config fields that changed
        config_changed = [f for f in self.fields if f.has_changed]

        # If anything changed, update it
        with self.project.open_session() as session:
            for field in config_changed:
                session.execute(
                    update(ConfigTbl).
                    where(ConfigTbl.key == field.config.name).
                    values(value=field.current_value)
                )
                field.save_state()

            # If any alias changed, just reload them all, because it's too
            # hard to make selective changes.
            if self.alias_list.has_changed():
                # Clear the table
                session.execute(delete(Aliases))
                # Add alias objects
                for e in self.alias_list.entries():
                    if e.has_contents():
                        print(f'sql: {e.to_sql_object()}')
                        session.add(e.to_sql_object())

                self.alias_list.save_changes()

            session.commit()

        # Forcibly reload the project config from the database
        self.project.config.read_from_db()


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
            preferences_dialog: The preferences dialog instance to which this
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

    def save_state(self) -> None:
        """
        Save the current state of this entry as the new 'initial' state.
        This basically resets self.has_changed to False.

        Returns:
            None
        """

        self.initial_value = self.current_value
        self.has_changed = False


class AliasList(QListWidget):
    """
    This widget contains the entire scrollable list of AliasEntries. The user
    can add new aliases to this list and remove or modify existing ones. When
    the preferences dialog is loaded, this is populated with the aliases
    currently saved in the project database.
    """

    def __init__(self, project: Project):
        """
        Create the AliasList.

        Args:
            project: The project the user has open.
        """

        super().__init__()

        # This tracks whether any items in the list were deleted
        self.any_deleted: bool = False

        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)

        # Add initial alias entry
        with project.open_session() as session:
            aliases = session.scalars(select(Aliases))
            for alias in aliases:
                self.new_entry(alias.from_track is not None,
                               alias.from_artist,
                               alias.from_track,
                               alias.to_artist,
                               alias.to_track)

        # If there's no aliases, add an empty one
        if not self.count():
            self.new_entry(True)

        # Get a copy of the current list of entries to check for changes later
        self.initial_list = self.entries().copy()

    def new_entry(self,
                  include_track: bool,
                  from_artist: str = '',
                  from_track: str = '',
                  to_artist: str = '',
                  to_track: str = '') -> None:
        """
        Add a new item to this list.

        Args:
            include_track: True iff a field for the track name should be
                           included.
            from_artist: The name of the artist to change.
            from_track: The name of the track to change.
            to_artist: The new name for the artist.
            to_track: The new name for the track.

        Returns:
            None
        """

        item = QListWidgetItem(self)
        entry = AliasEntry(self,
                           item,
                           include_track,
                           from_artist=from_artist,
                           from_track=from_track,
                           to_artist=to_artist,
                           to_track=to_track)
        item.setSizeHint(entry.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, entry)

        self.scrollToBottom()

    def entries(self) -> List[AliasEntry]:
        """
        Get a list of all the alias entries associated with this list.
        
        Returns:
            A list of alias entries.
        """

        return [self.itemWidget(self.item(i))
                for i in range(self.count())]

    def has_changed(self) -> bool:
        """
        Determine whether any of the alias entries have changed from their
        original state. If they have, return True. Otherwise, return False.

        Returns:
            True iff at least one alias entry was changed (or deleted) by the
            user.
        """

        if self.any_deleted:
            return True

        entries = self.entries()

        # This could indicate reordering
        if entries != self.initial_list:
            return True

        for e in entries:
            if e.has_changed():
                return True
        return False

    def save_changes(self) -> None:
        """
        After the user clicks 'Apply' or 'Ok', save the current state of all
        the fields as their new initial state to properly detect future
        changes.

        Returns:
            None
        """

        self.any_deleted = False
        self.initial_list = self.entries().copy()
        for e in self.initial_list:
            e.save_changes()

    def sizeHint(self) -> QSize:
        """
        Override sizeHint to hint proper width for alias entries. This is
        based on https://stackoverflow.com/questions/6337589/qlistwidget
        -adjust-size-to-content

        Returns:
            The size hint.
        """

        return QSize(self.sizeHintForColumn(0),
                     super().sizeHint().height())


class AliasLineEdit(QLineEdit):
    def __init__(self,
                 initial: str,
                 placeholder: str):
        """
        Initialize a changeable line edit.

        Args:
            initial: The initial text to display in the field.
            placeholder: The placeholder text to show when the field is empty.
        """

        super().__init__(initial)

        self.initial = initial
        self.setPlaceholderText(placeholder)

    def alias_text(self) -> Optional[str]:
        """
        Return the contents of this line edit, UNLESS it's empty, in which
        case None is returned instead.

        Returns:
              The contents of this line edit, or None.
        """
        return self.text() if self.text() != '' else None


class AliasEntry(QWidget):
    def __init__(self,
                 alias_list: AliasList,
                 item: QListWidgetItem,
                 include_track: bool,
                 from_artist: str,
                 from_track: str,
                 to_artist: str,
                 to_track: str):
        """
        Create an entry for the aliases list.

        Args:
            alias_list: The list containing this entry.
            item: The list item to which this widget will be attached. This
                  is used if the user removes this entry from the list.
            include_track: This determines whether a field for the track name
                           should be included. If it's False, there will only
                           be fields for the artist name.
            from_artist: The name of the artist to change.
            from_track: The name of the track to change.
            to_artist: The new name for the artist.
            to_track: The new name for the track.
        """
        super().__init__()

        self.alias_list = alias_list
        self.include_track = include_track
        self.item = item

        self.setContentsMargins(10, 0, 10, 0)

        # Create layouts
        lyt = QHBoxLayout()
        lyt_from = QHBoxLayout()
        lyt_to = QHBoxLayout()
        lyt.addLayout(lyt_from)
        lyt.addLayout(lyt_to)

        self.field_from_artist = AliasLineEdit(from_artist, 'Artist')
        self.field_to_artist = AliasLineEdit(to_artist, 'Artist')

        lyt_from.addWidget(QLabel('Change'))
        lyt_to.addWidget(QLabel('to'))

        lyt_from.addWidget(self.field_from_artist)
        lyt_to.addWidget(self.field_to_artist)

        if self.include_track:
            self.field_from_track = AliasLineEdit(from_track, 'Track')
            self.field_to_track = AliasLineEdit(to_track, 'Track')

            lyt_from.addWidget(self.field_from_track)
            lyt_to.addWidget(self.field_to_track)

        # Add button
        btn = CancelBtn(self.delete_entry)
        lyt.addWidget(btn)

        self.setLayout(lyt)

    def has_contents(self) -> bool:
        """
        Determine whether this alias field has contents.

        Returns:
            True if and only if at least one of the fields has text in it.
        """

        if self.field_from_artist.text() or self.field_to_artist.text():
            return True
        if self.include_track:
            if self.field_from_track.text() or self.field_to_track.text():
                return True

        return False

    def has_changed(self) -> bool:
        """
        Determine whether the fields in this entry have been changed by the
        user.

        Returns:
            True iff any of the fields were changed by the user.
        """

        if (self.field_from_artist.text() != self.field_from_artist.initial or
                self.field_to_artist.text() != self.field_to_artist.initial):
            return True
        if self.include_track:
            if (self.field_to_track.text() != self.field_to_track.initial or
                    self.field_from_track.text() !=
                    self.field_from_track.initial):
                return True

        return False

    def save_changes(self) -> None:
        """
        After the user clicks 'Apply' or 'Ok', save the current state of all
        the fields as their new initial state to properly detect future
        changes.

        Returns:
            None
        """

        self.field_from_artist.initial = self.field_from_artist.text()
        self.field_to_artist.initial = self.field_to_artist.text()
        if self.include_track:
            self.field_from_track.initial = self.field_from_track.text()
            self.field_to_track.initial = self.field_to_track.text()

    def to_sql_object(self) -> Aliases:
        """
        Create a SQLAlchemy object based on this AliasEntry in its current
        state.

        Returns:
            An object for sending to the SQLite database.
        """

        return Aliases(
            from_artist=self.field_from_artist.alias_text(),
            from_track=(self.field_from_track.alias_text()
                        if self.include_track else None),
            to_artist=self.field_to_artist.alias_text(),
            to_track=(self.field_to_track.alias_text()
                      if self.include_track else None)
        )

    def delete_entry(self) -> None:
        """
        This is called when the user clicks the 'X' in the alias entry. If
        this is not the only row in the list, then this row is deleted from
        the list.

        But if this is the last row left, then instead of being deleted,
        it is merely cleared. That way there's always at least one row.

        Returns:
            None
        """

        self.alias_list.any_deleted = True

        if self.alias_list.count() > 1:
            self.alias_list.takeItem(self.alias_list.row(self.item))
        else:
            self.field_from_artist.clear()
            self.field_to_artist.clear()
            if self.include_track:
                self.field_from_track.clear()
                self.field_to_track.clear()


def delete_items_of_layout(layout: QLayout) -> None:
    """
    Delete all the widgets in a layout. This was taken from
    https://stackoverflow.com/questions/37564728/pyqt-how-to-remove-a-layout
    -from-a-layout

    Args:
        layout: The layout whose contents will be deleted.

    Returns:
        None
    """

    if layout:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                delete_items_of_layout(item.layout())


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
