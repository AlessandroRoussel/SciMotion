"""
Service concerning the app in general.

The AppService focuses on the GUI app.
"""

import sys

from configparser import ConfigParser
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from utils.singleton import Singleton
from gui.views.app import App
from gui.views.main_window import MainWindow


class AppService(metaclass=Singleton):
    """Service concerning the app in general."""

    _title: str
    _version_major: int
    _version_minor: int
    _min_width: int
    _min_height: int

    _qt_style: str
    _full_screen: bool
    _second_screen: bool

    _app: App
    _main_window: MainWindow

    def __init__(self, config: ConfigParser):
        self._title = config.get("app", "title")
        self._version_major = config.getint("app", "version_major")
        self._version_minor = config.getint("app", "version_minor")
        self._min_width = config.getint("window", "min_width")
        self._min_height = config.getint("window", "min_height")

        self._qt_style = config.get("window", "qt_style")
        self._full_screen = config.getboolean("window", "full_screen")
        self._second_screen = config.getboolean("window", "second_screen")

    def initialize_app(self):
        """Initialize the app."""
        self._app = App()
        self._app.setStyle(
            QStyleFactory.create(self._qt_style))

        self._main_window = MainWindow()
        _screens = self._app.screens()
        if self._second_screen and len(_screens) > 1:
            _second_screen = _screens[1]
            _screen_geometry = _second_screen.geometry()
            self._main_window.move(
                _screen_geometry.left(), _screen_geometry.top())
        self.center_main_window()

        self.setup_main_window()
        self.show_main_window(self._full_screen)

        sys.exit(self._app.exec())

    def center_main_window(self):
        """Center the main window within the current screen."""
        _screen = self._main_window.screen()
        _screen_geometry = _screen.geometry()
        _screen_center = _screen_geometry.center()
        _qr = self._main_window.frameGeometry()
        _qr.moveCenter(_screen_center)
        self._main_window.move(_qr.topLeft())

    def setup_main_window(self):
        """Set up the main window."""
        _window = self._main_window
        _window.setWindowIcon(QIcon("icon.ico"))
        _title = (f"{self._title} {self._version_major}"
                  f".{self._version_minor}")
        _window.setWindowTitle(_title)
        _window.setMinimumSize(QSize(self._min_width, self._min_height))

    def show_main_window(self, maximized: bool):
        """Show the main window."""
        if maximized:
            self._main_window.showMaximized()
        else:
            self._main_window.show()
