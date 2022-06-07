from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QMainWindow


class CenteredWindow(QMainWindow):
    def __init__(self, page_layout):
        """
        Create a new CenteredWindow. Specify the layout object that will
        contain all the widgets. This layout will be embedded in a QFrame to
        control it maximum height while still allowing the whole window to be
        expanded.

        After populating the layout, call .set_fixed_size() to calculate the
        page size and set it as the frame maximum.

        Args:
            page_layout: The layout containing everything in the window.
        """

        super().__init__()

        self._frame = QFrame()
        self.layout = page_layout
        self._frame.setLayout(self.layout)

        base_layout = QVBoxLayout(self)
        base_layout.addWidget(self._frame)
        base_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter |
                                 Qt.AlignmentFlag.AlignVCenter)

        base_widget = QWidget()
        base_widget.setLayout(base_layout)

        self.setCentralWidget(base_widget)

    def set_fixed_size(self) -> None:
        """
        Fix the maximum size of this window to enable proper centering.

        Returns:
            None
        """

        self._frame.setMaximumHeight(self.layout.sizeHint().height())
