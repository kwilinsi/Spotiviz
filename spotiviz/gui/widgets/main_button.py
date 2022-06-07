from PyQt6.QtWidgets import QPushButton, QSizePolicy


class MainButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)

        self.setMinimumSize(130, 40)
        self.setMaximumSize(175, 40)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Expanding)