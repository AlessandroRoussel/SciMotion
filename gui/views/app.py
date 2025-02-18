"""Main QApplication for the app."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from gui.views.main_window import MainWindow
from core.entities.gl_context import GLContext
from utils.config import Config


class App(QApplication):
    """Main QApplication for the app."""

    def __init__(self):
        """Initialize the app."""
        self.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        self.setAttribute(Qt.AA_EnableHighDpiScaling)
        super().__init__()

        GLContext.get_context()
        _main_window = MainWindow()
        _screens = self.screens()
        if Config.window.second_screen and len(_screens) > 1:
            _second_screen = _screens[1]
            _screen_geometry = _second_screen.geometry()
            _main_window.move(_screen_geometry.left(), _screen_geometry.top())
        _main_window.center()
        if Config.window.full_screen:
            _main_window.showMaximized()
        else:
            _main_window.show()
        sys.exit(self.exec())