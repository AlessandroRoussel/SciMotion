"""Main window of the app."""

from typing import Callable

from PySide6.QtGui import QIcon, QKeySequence, QAction
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter,
                               QFrame, QStatusBar, QLayout)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from utils.config import Config
from gui.views.main_tool_bar import MainToolBar
from gui.views.viewer.viewer_pane import ViewerPane
from gui.views.explorer.explorer_pane import ExplorerPane
from gui.views.timeline.timeline_pane import TimelinePane
from gui.views.misc.misc_pane import MiscPane
from gui.services.sequence_gui_service import SequenceGUIService


class MainWindow(QMainWindow):
    """Main window of the app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("{0} {1}.{2}".format(
            Config().app.title,
            Config().app.version_major,
            Config().app.version_minor
        ))
        self.setMinimumSize(QSize(Config().window.min_width,
                                  Config().window.min_height))
        self.setWindowIcon(QIcon(Config().app.icon))
        
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _main_widget = QWidget()
        _main_widget.setLayout(_layout)
        self.setCentralWidget(_main_widget)

        _panes = self.create_main_panes()
        _layout.addWidget(_panes)

        self.setStatusBar(QStatusBar(self))
        self.create_menu_bar()
        _tool_bar = MainToolBar(self)
        self.addToolBar(_tool_bar)

        self.initialize_open_gl_context(_layout)
    
    def center(self):
        """Center the window in the current screen."""
        _screen = self.screen()
        _screen_geometry = _screen.geometry()
        _screen_center = _screen_geometry.center()
        _qr = self.frameGeometry()
        _qr.moveCenter(_screen_center)
        self.move(_qr.topLeft())

    def create_menu_bar(self):
        """Create the menu bar."""
        _menu = self.menuBar()

        # File menu
        _file = _menu.addMenu("&File")
        _file.addAction(self.create_action("New project", None))
        _file.addAction(self.create_action("Open project", None, "Ctrl+O"))
        _file.addSeparator()
        _file.addAction(self.create_action("Save project", None, "Ctrl+S"))
        _file.addAction(self.create_action("Save project as", None, "Ctrl+Shift+S"))
        _file.addSeparator()
        _file.addAction(self.create_action("Project parameters", None, "Ctrl+P"))
        _file.addSeparator()
        _file.addAction(self.create_action("Close", None, "Ctrl+Q"))

        # Edit menu
        _edit = _menu.addMenu("&Edit")
        _edit.addAction(self.create_action("Cut", None, "Ctrl+X"))
        _edit.addAction(self.create_action("Copy", None, "Ctrl+C"))
        _edit.addAction(self.create_action("Paste", None, "Ctrl+V"))

        # Sequence menu
        _sequence = _menu.addMenu("&Sequence")
        _sequence.addAction(
            self.create_action("New sequence",
                               SequenceGUIService.create_new_sequence,
                               "Ctrl+N"))
        _sequence.addSeparator()
        _sequence.addAction(self.create_action("Sequence parameters", None))
        
        # Layer menu
        _layer = _menu.addMenu("&Layer")
        _layer.addAction(self.create_action("New solid layer", None, "Ctrl+Y"))
        _layer.addSeparator()
        _layer.addAction(self.create_action("Layer parameters", None, "Ctrl+Shift+Y"))

    def create_action(self,
                      title: str,
                      function: Callable,
                      shortcut: str = None
                      ) -> QAction:
        """Create a QAction for the menu bar."""
        _action = QAction(title, self)
        _action.setStatusTip(title)
        _action.triggered.connect(function)
        if shortcut is not None:
            _action.setShortcut(QKeySequence(shortcut))
        return _action

    def create_main_panes(self) -> QSplitter:
        """Create the main panes and splitters."""
        _explorer = ExplorerPane(self)
        _viewer = ViewerPane(self)
        _timeline = TimelinePane(self)
        _misc = MiscPane(self)

        _top = QSplitter(Qt.Horizontal, self)
        _left = QSplitter(Qt.Vertical, self)
        _main = QSplitter(Qt.Horizontal, self)

        _top.addWidget(_explorer)
        _top.addWidget(_viewer)
        _left.addWidget(_top)
        _left.addWidget(_timeline)
        _main.addWidget(_left)
        _main.addWidget(_misc)

        _top.setStretchFactor(0, 0)
        _top.setStretchFactor(1, 1)
        _left.setStretchFactor(0, 1)
        _left.setStretchFactor(1, 0)
        _main.setStretchFactor(0, 1)
        _main.setStretchFactor(1, 0)

        _top.setSizes([Config().window.left_pane_width, 100])
        _left.setSizes([100, Config().window.bottom_pane_height])
        _main.setSizes([100, Config().window.right_pane_width])

        _top.setHandleWidth(Config().window.splitter_width)
        _left.setHandleWidth(Config().window.splitter_width)
        _main.setHandleWidth(Config().window.splitter_width)
        return _main
    
    def initialize_open_gl_context(self, layout: QLayout):
        """Create and remove an OpenGL widget to initialize the context."""
        _first_open_gl_context = QOpenGLWidget()
        _first_open_gl_context.hide()
        layout.addWidget(_first_open_gl_context)
        layout.removeWidget(_first_open_gl_context)
        del _first_open_gl_context