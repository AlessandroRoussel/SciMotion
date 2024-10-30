"""Main tool bar of the app."""

from PySide6.QtWidgets import QToolBar, QWidget

class MainToolBar(QToolBar):
    """Main tool bar of the app."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setMovable(False)