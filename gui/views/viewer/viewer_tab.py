"""
A tab for viewing an image or video sequence.

The ViewerTab inherits from QFrame and provides the user with
a visualization tab within the ViewerPane. It holds a GLViewer
widget which displays images with OpenGL.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QComboBox, QVBoxLayout, QToolBar,
                               QWidget, QCheckBox)
from PySide6.QtGui import QWheelEvent, QCursor

from gui.views.viewer.gl_viewer import GLViewer
from gui.services.sequence_gui_service import SequenceGUIService


class ViewerTab(QFrame):
    """A tab for viewing an image or video sequence."""

    _sequence_id: int
    _gl_viewer: GLViewer
    _zoom_list: QComboBox
    _zoom_list_length: int

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        self._gl_viewer = GLViewer(self)
        self._gl_viewer.wheelEvent = self.scroll_gl_viewer
        _tool_bar = self.create_tool_bar()

        _layout.addWidget(self._gl_viewer)
        _layout.addWidget(_tool_bar)

        self._gl_viewer.set_image(
            SequenceGUIService.request_image_from_sequence(sequence_id, 0))
        self._zoom_list.setCurrentIndex(1)
    
    def scroll_gl_viewer(self, event: QWheelEvent):
        """Handle scrolling the GLViewer."""
        self._gl_viewer.wheel_scroll(event)
        self.update_zoom_value()

    def create_tool_bar(self) -> QToolBar:
        """Create the viewer tool bar."""
        _tool_bar = QToolBar("Viewer toolbar", self)
        _base_color = self.palette().base().color()
        _tool_bar.setStyleSheet("QToolBar {"
                                f"background-color: {_base_color.name()};"
                                "}")

        # Zoom list combo box:
        self._zoom_list = QComboBox(self)
        self._zoom_list.setCursor(QCursor(Qt.PointingHandCursor))
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

        _tool_bar.addSeparator()

        # Transparency checkerboard checkbox:
        _alpha_checkbox = QCheckBox("Transparency")
        _alpha_checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        _alpha_checkbox.checkStateChanged.connect(self.toggle_checkerboard)
        _tool_bar.addWidget(_alpha_checkbox)
        _alpha_checkbox.setCheckState(Qt.CheckState.Checked)

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
        _current_zoom_index = self._zoom_list.findText(_text)
        if _current_zoom_index == -1:
            self._zoom_list.addItem(_text)
            self._zoom_list.setCurrentIndex(self._zoom_list_length)
        else:
            self._zoom_list.setCurrentIndex(_current_zoom_index)
        self._zoom_list.blockSignals(False)

    def toggle_checkerboard(self, state: Qt.CheckState):
        """Manage transparency checkbox toggle."""
        self._gl_viewer.toggle_checkerboard(state is Qt.CheckState.Checked)
