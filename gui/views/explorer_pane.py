from PyQt5.QtWidgets import QFrame
from gui.views.main_window import MainWindow


class ExplorerPane(QFrame):
    def __init__(self, main_window: MainWindow):
        super(QFrame, self).__init__(main_window)
        self.setFrameShape(QFrame.StyledPanel)
