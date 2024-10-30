"""
Service concerning the app in general.

The AppService focuses on the GUI app.
"""

import sys

from PySide6.QtWidgets import QApplication, QStyleFactory
from gui.views.main_window import MainWindow

from utils.singleton import Singleton
from utils.config import Config


class AppService(metaclass=Singleton):
    """Service concerning the app in general."""

    def initialize_app(self):
        """Initialize the app."""
        _app = QApplication()
        _main_window = MainWindow()
        _screens = _app.screens()
        if Config().window.second_screen and len(_screens) > 1:
            _second_screen = _screens[1]
            _screen_geometry = _second_screen.geometry()
            _main_window.move(_screen_geometry.left(), _screen_geometry.top())
        _main_window.center()
        if Config().window.full_screen:
            _main_window.showMaximized()
        else:
            _main_window.show()
        sys.exit(_app.exec())