"""
Service concerning the app in general.

The AppService focuses on the GUI app.
"""

import sys
from typing import Callable

from configparser import ConfigParser
from PyQt5.QtWidgets import (QStyleFactory, QStatusBar, QWidget, QVBoxLayout,
                             QToolBar, QLayout, QAction, QSplitter)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import QSize, Qt

from utils.singleton import Singleton
from gui.views.app import App
from gui.views.main_window import MainWindow
from gui.services.action_service import ActionService
from gui.views.explorer_pane import ExplorerPane
from gui.views.viewer_pane import ViewerPane
from gui.views.timeline_pane import TimelinePane
from gui.views.misc_pane import MiscPane


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
    _splitter_width: int
    _left_pane_width: int
    _right_pane_width: int
    _bottom_pane_height: int

    _app: App
    _main_window: MainWindow
    _explorer_pane: ExplorerPane
    _viewer_pane: ViewerPane
    _timeline_pane: TimelinePane
    _misc_pane: MiscPane

    def __init__(self, config: ConfigParser):
        self._title = config.get("app", "title")
        self._version_major = config.getint("app", "version_major")
        self._version_minor = config.getint("app", "version_minor")
        self._min_width = config.getint("window", "min_width")
        self._min_height = config.getint("window", "min_height")

        self._qt_style = config.get("window", "qt_style")
        self._full_screen = config.getboolean("window", "full_screen")
        self._second_screen = config.getboolean("window", "second_screen")
        self._splitter_width = config.getint("window", "splitter_width")
        self._left_pane_width = config.getint("window", "left_pane_width")
        self._right_pane_width = config.getint("window", "right_pane_width")
        self._bottom_pane_height = config.getint("window",
                                                 "bottom_pane_height")

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
        self.create_main_window_ui()
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

    def create_main_window_ui(self):
        """Create the UI layout of the MainWindow."""
        _window = self._main_window
        _main_panes = self.create_main_window_panes()
        _layout = self.create_main_window_layout()
        _layout.addWidget(_main_panes)
        _window.setStatusBar(QStatusBar(_window))
        self.create_tool_bar()
        self.create_menu_bar()

    def create_main_window_layout(self) -> QLayout:
        """Create the layout for the MainWindow."""
        _main_widget = QWidget()
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _main_widget.setLayout(_layout)
        self._main_window.setCentralWidget(_main_widget)
        return _layout

    def create_tool_bar(self):
        """Create the tool bar for the MainWindow."""
        _tool_bar = QToolBar("Tool bar")
        _tool_bar.setMovable(False)
        self._main_window.addToolBar(_tool_bar)

    def create_menu_bar(self):
        """Create the menu bar for the MainWindow."""
        _window = self._main_window
        _menu_bar = _window.menuBar()

        # File menu
        _file_menu = _menu_bar.addMenu("&File")
        _file_menu.addAction(self.create_action(
            "New project", ActionService().create_new_project, "Ctrl+N"))
        _file_menu.addAction(self.create_action(
            "Open project", ActionService().open_project, "Ctrl+O"))
        _file_menu.addSeparator()
        _file_menu.addAction(self.create_action(
            "Save project", ActionService().save_project, "Ctrl+S"))
        _file_menu.addAction(self.create_action(
            "Save project as",
            ActionService().save_project_as,
            "Ctrl+Shift+S"))
        _file_menu.addSeparator()
        _file_menu.addAction(self.create_action(
            "Project parameters",
            ActionService().open_project_parameters,
            "Ctrl+P"))
        _file_menu.addSeparator()
        _file_menu.addAction(self.create_action(
            "Close", ActionService().close, "Ctrl+Q"))

        # Edit menu
        _edit_menu = _menu_bar.addMenu("&Edit")
        _edit_menu.addAction(self.create_action(
            "Cut", ActionService().cut, "Ctrl+X"))
        _edit_menu.addAction(self.create_action(
            "Copy", ActionService().copy, "Ctrl+C"))
        _edit_menu.addAction(self.create_action(
            "Paste", ActionService().paste, "Ctrl+V"))

    def create_action(self,
                      title: str,
                      function: Callable,
                      shortcut: str = None
                      ) -> QAction:
        """Create a QAction."""
        _action = QAction(title, self._main_window)
        _action.setStatusTip(title)
        _action.triggered.connect(function)
        if shortcut is not None:
            _action.setShortcut(QKeySequence(shortcut))
        return _action

    def create_main_window_panes(self) -> QSplitter:
        """Create the UI panes for the MainWindow."""
        self._explorer_pane = ExplorerPane(self._main_window)
        self._viewer_pane = ViewerPane(self._main_window)
        self._timeline_pane = TimelinePane(self._main_window)
        self._misc_pane = MiscPane(self._main_window)

        _top_pane = QSplitter(Qt.Horizontal)
        _left_pane = QSplitter(Qt.Vertical)
        _main_pane = QSplitter(Qt.Horizontal)

        _top_pane.setHandleWidth(self._splitter_width)
        _left_pane.setHandleWidth(self._splitter_width)
        _main_pane.setHandleWidth(self._splitter_width)

        _top_pane.addWidget(self._explorer_pane)
        _top_pane.addWidget(self._viewer_pane)
        _left_pane.addWidget(_top_pane)
        _left_pane.addWidget(self._timeline_pane)
        _main_pane.addWidget(_left_pane)
        _main_pane.addWidget(self._misc_pane)

        _top_pane.setStretchFactor(0, 0)
        _top_pane.setStretchFactor(1, 1)
        _left_pane.setStretchFactor(1, 0)
        _left_pane.setStretchFactor(0, 1)
        _main_pane.setStretchFactor(1, 0)
        _main_pane.setStretchFactor(0, 1)

        _top_pane.setSizes([self._left_pane_width, 100])
        _left_pane.setSizes([100, self._bottom_pane_height])
        _main_pane.setSizes([100, self._right_pane_width])
        return _main_pane
