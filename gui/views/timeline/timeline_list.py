"""
The layer list panel of a TimelineTab.

The TimelineList provides the user with the list of layers and their
properties, it sits alongside a TimelineView within a TimelineTab.
"""

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy,
                               QScrollArea, QFrame)

from utils.config import Config
from utils.notification import Notification
from core.entities.sequence import Sequence


class TimelineList(QScrollArea):
    """The layer list panel of a TimelineTab."""

    _sequence: Sequence
    _layer_line_list: list[QLabel]
    _layout: QVBoxLayout
    _middle_mouse_pressed: bool
    _prev_mouse_pos: QPointF

    _y_offset: float
    y_offset_signal: Notification

    def __init__(self, parent: QWidget, sequence: Sequence):
        super().__init__(parent)

        self._sequence = sequence
        self._y_offset = 0
        self._middle_mouse_pressed = False
        self.y_offset_signal = Notification()
        self._layer_line_list = []

        _widget = QWidget(self)
        self.setWidget(_widget)
        self.setWidgetResizable(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(Config.timeline.layer_spacing)
        self._layout.setContentsMargins(0, 0, 0, 0)
        _widget.setLayout(self._layout)

        self.setFocusPolicy(Qt.WheelFocus)

    def update_layers(self):
        """Update the display of the layers."""
        # TODO : not destroy all layers and rebuild
        self.clear_all()
        _layer_height = Config.timeline.layer_height
        _layer_list = self._sequence.get_layer_list()
        for _i in range(len(_layer_list)):
            _layer = _layer_list[len(_layer_list) - 1 - _i]
            _layer_title = _layer.get_title()
            _layer_line = QLabel(f"{_layer_title}")
            _layer_line.setFixedHeight(_layer_height)
            _layer_line.setStyleSheet("background-color: lightgray;"
                                      "padding: 5px;"
                                      "color: black;")
            self._layer_line_list.append(_layer_line)
            self._layout.addWidget(_layer_line)

    def clear_all(self):
        """Remove all layers."""
        for _layer_line in self._layer_line_list:
            self._layout.removeWidget(_layer_line)
            _layer_line.deleteLater()
            _layer_line = None
        self._layer_line_list = []

    def wheelEvent(self, event: QWheelEvent):
        """Override the wheel event."""
        _delta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            return
        _y_offset = self._y_offset-_delta*Config.timeline.scroll_sensitivity
        self.y_offset_signal.emit(_y_offset)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if event.button() == Qt.MiddleButton:
            self._middle_mouse_pressed = True
            self._prev_mouse_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle the mouse move event."""
        if self._middle_mouse_pressed:
            _mouse_pos = event.position()
            _delta = _mouse_pos - self._prev_mouse_pos
            self.y_offset_signal.emit(self._y_offset - _delta.y())
            self._prev_mouse_pos = _mouse_pos

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self._middle_mouse_pressed = False
            self.setCursor(Qt.ArrowCursor)
    
    def set_y_offset(self, y_offset: float):
        """Set the y offset value."""
        self._y_offset = y_offset
        self.verticalScrollBar().setValue(y_offset)