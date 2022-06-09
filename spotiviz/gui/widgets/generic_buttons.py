from PyQt6.QtWidgets import QPushButton, QSizePolicy


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
