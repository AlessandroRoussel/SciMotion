"""
A tab for viewing a sequence timeline.

The TimelineTab inherits from QFrame and provides the user with
a visual timeline within the TimelinePane.
"""

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (QFrame, QWidget, QSplitter, QVBoxLayout,
                               QScrollArea, QScrollBar)

from gui.views.timeline.timeline_view import TimelineView
from gui.views.timeline.timeline_side import TimelineSide
from utils.config import Config


class TimelineTab(QFrame):
    """A tab for viewing a sequence timeline."""

    _sequence_id: int
    _side: TimelineSide
    _view: TimelineView
    _scroll_area: QScrollArea
    _splitter: QSplitter
    _bottom_splitter: QSplitter
    _horizontal_scroll_bar: QWidget

    _mouse_middle_dragging: bool
    _mouse_last_position: QPointF

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id

        # Side and view layout:
        self._side = TimelineSide(self)
        self._view = TimelineView(self, sequence_id)

        self._splitter = QSplitter(Qt.Horizontal, self)
        self._splitter.addWidget(self._side)
        self._splitter.addWidget(self._view)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([Config().timeline.side_panel_width, 100])
        self._splitter.setHandleWidth(Config().window.splitter_width)

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._splitter)

        # Bottom bar layout:

        _empty_widget = QWidget(self)
        self._horizontal_scroll_bar = QScrollBar(Qt.Horizontal, self)
        self._horizontal_scroll_bar.setSingleStep(20)
        self._horizontal_scroll_bar.setPageStep(100)
        self._horizontal_scroll_bar.valueChanged.connect(
            self.horizontal_scrollbar_changed)
        _view_scroll_bar = self._view.horizontalScrollBar()
        _view_scroll_bar.rangeChanged.connect(
            self.update_horizontal_range)
        self._view.page_step_changed_signal.connect(
            self.update_horizontal_page_step)
        self.update_horizontal_range(_view_scroll_bar.minimum(),
                                     _view_scroll_bar.maximum())
        self.update_horizontal_page_step(_view_scroll_bar.pageStep())
        
        self._bottom_splitter = QSplitter(Qt.Horizontal, self)
        self._bottom_splitter.addWidget(_empty_widget)
        self._bottom_splitter.addWidget(self._horizontal_scroll_bar)
        self._bottom_splitter.setStretchFactor(0, 0)
        self._bottom_splitter.setStretchFactor(1, 1)
        self._bottom_splitter.setSizes(
            [Config().timeline.side_panel_width, 100])
        self._bottom_splitter.setHandleWidth(0)
        for _i in range(self._bottom_splitter.count()):
            self._bottom_splitter.handle(_i).setEnabled(False)
        self._splitter.splitterMoved.connect(self.synchronize_splitters)

        # Main layout:
        _layout = QVBoxLayout()
        _layout.addWidget(self._scroll_area)
        _layout.addWidget(self._bottom_splitter)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        # User interactions:
        self._mouse_middle_dragging = False
        self._mouse_last_position = None
        self._view.middle_mouse_press_signal.connect(
            self.on_middle_mouse_press)
        self._side.middle_mouse_press_signal.connect(
            self.on_middle_mouse_press)
        self._view.middle_mouse_release_signal.connect(
            self.on_middle_mouse_release)
        self._side.middle_mouse_release_signal.connect(
            self.on_middle_mouse_release)
        self._view.mouse_move_signal.connect(
            self.on_mouse_move)
        self._side.mouse_move_signal.connect(
            self.on_mouse_move)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if event.button() == Qt.MiddleButton:
            self.on_middle_mouse_press(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self.on_middle_mouse_release(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle the mouse move event."""
        self.on_mouse_move(event)

    def on_middle_mouse_press(self, event: QMouseEvent):
        """Handle middle mouse press event."""
        self._mouse_middle_dragging = True
        self._mouse_last_position = event.globalPosition()
        self.setCursor(Qt.ClosedHandCursor)
    
    def on_middle_mouse_release(self, event: QMouseEvent):
        """Handle middle mouse release event."""
        self._mouse_middle_dragging = False
        self.setCursor(Qt.ArrowCursor)
    
    def on_mouse_move(self, event: QMouseEvent):
        """Handle middle mouse move event."""
        if self._mouse_middle_dragging:
            _current_pos = event.globalPosition()
            _delta = _current_pos - self._mouse_last_position
            self.on_middle_mouse_button_drag(_delta)
            self._mouse_last_position = _current_pos

    def on_middle_mouse_button_drag(self, delta: float):
        """Drag using middle mouse button."""
        _vert_scroll_bar = self._scroll_area.verticalScrollBar()
        _vert_scroll_bar.setValue(_vert_scroll_bar.value() - delta.y())
        self._horizontal_scroll_bar.setValue(
            self._horizontal_scroll_bar.value() - delta.x())

    def synchronize_splitters(self):
        """Synchronize the positions of both splitters."""
        _sizes = self._splitter.sizes()
        self._bottom_splitter.setSizes(_sizes)

    def horizontal_scrollbar_changed(self, value: int):
        """Handle scrolling the horizontal scroll bar."""
        self._view.horizontalScrollBar().setValue(value)

    def update_horizontal_range(self, min: int, max: int):
        """Update the horizontal scroll bar range."""
        self._horizontal_scroll_bar.setRange(min, max)

    def update_horizontal_page_step(self, page_step: int):
        """Update the horizontal scroll bar page step."""
        self._horizontal_scroll_bar.setPageStep(page_step)
