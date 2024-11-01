"""
The properties side panel of a TimelineTab.

The TimelineSide inherits provides the user with the list of layers and
their properties, it sits alongside a TimelineView within a TimelineTab.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy)

from utils.config import Config
from utils.notification import Notification


class TimelineSide(QWidget):
    """The properties side panel of a TimelineTab."""
    
    middle_mouse_press_signal: Notification
    middle_mouse_release_signal: Notification
    mouse_move_signal: Notification

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.middle_mouse_press_signal = Notification()
        self.middle_mouse_release_signal = Notification()
        self.mouse_move_signal = Notification()
        
        _layout = QVBoxLayout(self)
        _layout.setAlignment(Qt.AlignTop)
        _layout.setSpacing(Config().timeline.layer_spacing)
        _layout.setContentsMargins(0, 1, 0, 1)
        self.setLayout(_layout)

        for i in range(20):
            _layer = QLabel(f"Layer {i + 1}")
            _layer.setFixedHeight(Config().timeline.layer_height)
            _layer.setStyleSheet("background-color: lightgray;"
                                 "padding: 5px;"
                                 "color: black;")
            _layout.addWidget(_layer)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_press_signal.emit(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle the mouse move event."""
        self.mouse_move_signal.emit(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self.middle_mouse_release_signal.emit(event)