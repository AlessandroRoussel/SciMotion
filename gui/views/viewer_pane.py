"""
A pane for viewing images and video sequences.

The ViewerPane inherits from QFrame and provides the user with
an interactive visualization pane for viewing sequences and media.
It holds a GLViewer widget which displays images with OpenGL.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QComboBox, QVBoxLayout, QToolBar,
                               QWidget)
from PySide6.QtGui import QWheelEvent

from gui.views.gl_viewer import GLViewer


class ViewerPane(QFrame):
    """A pane for viewing images and video sequences."""

    _gl_viewer: GLViewer
    _zoom_list: QComboBox
    _zoom_list_length: int

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        self._gl_viewer = GLViewer(self)
        self.link_gl_viewer_function()
        _tool_bar = self.create_tool_bar()

        _layout.addWidget(self._gl_viewer)
        _layout.addWidget(_tool_bar)
    
    def link_gl_viewer_function(self):
        """Link GLViewer functions to ViewerPane functions."""
        self._gl_viewer.wheelEvent = self.scroll_gl_viewer
    
    def scroll_gl_viewer(self, event: QWheelEvent):
        """Handle scrolling the GLViewer pane."""
        self._gl_viewer.wheel_scroll(event)
        self.update_zoom_value()

    def create_tool_bar(self) -> QToolBar:
        """Create the viewer tool bar."""
        _tool_bar = QToolBar("Viewer toolbar", self)
        self._zoom_list = QComboBox(self)
        self._zoom_list.addItem("Fit to frame")
        self._zoom_list.addItem("Fit up to 100%")
        
        self._zoom_list.insertSeparator(2)
        
        self._zoom_list.addItem("50%")
        self._zoom_list.addItem("100%")
        self._zoom_list.addItem("200%")
        
        self._zoom_list_length = self._zoom_list.count()
        self._zoom_list.currentIndexChanged.connect(self.choose_zoom)
        
        _tool_bar.addWidget(self._zoom_list)
        self._zoom_list.setCurrentIndex(4)
        _tool_bar.setOrientation(Qt.Horizontal)
        return _tool_bar
    
    def choose_zoom(self, index: int):
        """Choose a value in the zoom list."""
        self.remove_custom_zoom()
        if index == 0:
            self._gl_viewer.fit_to_frame()
        elif index == 1:
            self._gl_viewer.fit_to_frame(max_zoom=1)
        elif index == 3:
            self._gl_viewer.choose_zoom(.5)
            self.update_zoom_value()
        elif index == 4:
            self._gl_viewer.choose_zoom(1)
            self.update_zoom_value()
        elif index == 5:
            self._gl_viewer.choose_zoom(2)
            self.update_zoom_value()

    def remove_custom_zoom(self):
        """Remove the custom zoom option in the zoom list."""
        self._zoom_list.blockSignals(True)
        if self._zoom_list.count() > self._zoom_list_length:
            self._zoom_list.removeItem(self._zoom_list_length)
        self._zoom_list.blockSignals(False)

    def update_zoom_value(self):
        """Update the currently displayed zoom value."""
        _zoom = self._gl_viewer.get_zoom()
        self.remove_custom_zoom()
        self._zoom_list.blockSignals(True)
        _text = f"{round(_zoom*100)}%"
        if self._zoom_list.findText(_text) == -1:
            self._zoom_list.addItem(_text)
            self._zoom_list.setCurrentIndex(self._zoom_list_length)
        self._zoom_list.blockSignals(False)
