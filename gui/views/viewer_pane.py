"""
A pane for viewing images and video sequences.

The ViewerPane inherits from QFrame and provides the user with
an interactive visualization pane for viewing sequences and media.
It holds a GLViewer widget which displays images with OpenGL.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QComboBox, QVBoxLayout, QToolBar,
                               QWidget)

from gui.views.gl_viewer import GLViewer


class ViewerPane(QFrame):
    """A pane for viewing images and video sequences."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        _gl_viewer = GLViewer(self)
        _tool_bar = self.create_tool_bar()

        _layout.addWidget(_gl_viewer)
        _layout.addWidget(_tool_bar)
    
    def create_tool_bar(self) -> QToolBar:
        """Create the viewer tool bar."""
        _tool_bar = QToolBar("Viewer toolbar", self)
        _zoom_list = QComboBox(self)
        _zoom_list.addItem("Fit to frame")
        _zoom_list.addItem("Fit up to 100%")
        
        _zoom_list.insertSeparator(2)
        
        _zoom_list.addItem("50%")
        _zoom_list.addItem("100%")
        _zoom_list.addItem("200%")
        
        #_zoom_list.currentIndexChanged.connect(self.chooseZoom)
        _zoom_list_length = _zoom_list.count()
        
        _tool_bar.addWidget(_zoom_list)
        _zoom_list.setCurrentIndex(4)
        _tool_bar.setOrientation(Qt.Horizontal)
        return _tool_bar