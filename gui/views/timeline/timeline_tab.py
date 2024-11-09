"""
A tab for viewing a sequence timeline.

The TimelineTab inherits from QFrame and provides the user with
a visual timeline within the TimelinePane.
"""

from PySide6.QtCore import Qt, QPointF, QPoint
from PySide6.QtWidgets import (QFrame, QWidget, QSplitter, QVBoxLayout,
                               QGridLayout, QScrollBar, QSlider, QHBoxLayout)

from utils.config import Config
from core.services.project_service import ProjectService
from core.entities.sequence import Sequence
from gui.views.timeline.timeline_view import TimelineView
from gui.views.timeline.timeline_list import TimelineList


class TimelineTab(QFrame):
    """A tab for viewing a sequence timeline."""

    _sequence_id: int
    _sequence: Sequence
    _x_offset: float
    _y_offset: float
    _x_zoom: float
    _current_frame: int
    _stack_height: float

    _h_scroll_bar: QScrollBar
    _v_scroll_bar: QScrollBar
    _zoom_slider: QSlider
    _list: TimelineList
    _view: TimelineView

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id
        self._sequence = ProjectService.get_sequence_by_id(sequence_id)
        self._x_offset = 0
        self._y_offset = 0
        self._x_zoom = 1
        self._stack_height = 0
        self._current_frame = 0
        self.setFocusPolicy(Qt.StrongFocus)

        # Right panel:
        _right_widget = QWidget(self)
        _right_layout = QGridLayout(_right_widget)
        
        self._view = TimelineView(self, self._sequence)
        _right_layout.addWidget(self._view, 0, 0)

        _horizontal_scroll_layout = QGridLayout()
        _horizontal_scroll_layout.setContentsMargins(0, 0, 0, 0)
        _horizontal_scroll_layout.setSpacing(0)
        _right_layout.addLayout(_horizontal_scroll_layout, 1, 0)

        self._zoom_slider = QSlider(Qt.Horizontal, self)
        self._zoom_slider.setRange(0, 100)
        self._zoom_slider.setTickInterval(1)
        self._zoom_slider.setValue(0)
        _horizontal_scroll_layout.addWidget(self._zoom_slider, 0, 0)
        _horizontal_scroll_layout.setColumnStretch(0, 0)
        _horizontal_scroll_layout.setColumnStretch(1, 1)

        self._h_scroll_bar = QScrollBar(Qt.Horizontal, self)
        _horizontal_scroll_layout.addWidget(self._h_scroll_bar, 0, 1)
        _right_layout.setRowMinimumHeight(
            1, max(self._h_scroll_bar.sizeHint().height(),
                   self._zoom_slider.sizeHint().height()))

        _vert_scroll_widget = QWidget(self)
        _vert_scroll_layout = QVBoxLayout(_vert_scroll_widget)
        _vert_scroll_layout.setContentsMargins(0,0,0,0)
        _vert_scroll_layout.setSpacing(0)
        _right_layout.addWidget(_vert_scroll_widget, 0, 1)

        _empty_widget = QWidget(self)
        _empty_widget.setFixedHeight(Config.timeline.ruler_height)
        _vert_scroll_layout.addWidget(_empty_widget)

        self._v_scroll_bar = QScrollBar(Qt.Vertical, self)
        _right_layout.setColumnMinimumWidth(
            1, self._v_scroll_bar.sizeHint().width())
        _vert_scroll_layout.addWidget(self._v_scroll_bar)

        _right_layout.setRowStretch(0, 1)
        _right_layout.setColumnStretch(0, 1)
        _right_layout.setContentsMargins(0,0,0,0)
        _right_layout.setSpacing(0)

        # Left panel:
        _left_widget = QWidget(self)
        _left_layout = QGridLayout(_left_widget)
        self._list = TimelineList(self, self._sequence)
        _left_layout.addWidget(self._list, 1, 0)
        _left_layout.setRowStretch(1, 1)
        _left_layout.setRowMinimumHeight(0, Config.timeline.ruler_height)
        _left_layout.setRowMinimumHeight(
            2, self._h_scroll_bar.sizeHint().height())
        _left_layout.setContentsMargins(0,0,0,0)
        _left_layout.setSpacing(0)

        # Splitter:
        _splitter = QSplitter(Qt.Horizontal, self)
        _splitter.addWidget(_left_widget)
        _splitter.addWidget(_right_widget)
        _splitter.setStretchFactor(0, 0)
        _splitter.setStretchFactor(1, 1)
        _splitter.setSizes([Config.timeline.side_panel_width, 100])
        _splitter.setHandleWidth(Config.window.splitter_width)

        _layout = QVBoxLayout(self)
        _layout.addWidget(_splitter)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        # Initialize connections:
        self.set_x_zoom(0)
        self._h_scroll_bar.valueChanged.connect(self.horiz_scroll_bar_moved)
        self._v_scroll_bar.valueChanged.connect(self.vert_scroll_bar_moved)
        self._zoom_slider.valueChanged.connect(self.zoom_slider_moved)
        self._view.resize_signal.connect(self.handle_view_resized)
        self._view.x_offset_signal.connect(self.set_x_offset)
        self._view.y_offset_signal.connect(self.set_y_offset)
        self._list.y_offset_signal.connect(self.set_y_offset)
        self._view.x_zoom_signal.connect(self.set_x_zoom)
        self._view.stack_height_signal.connect(self.set_stack_height)

        self._list.update_layers()
        self._view.update_layers()
    
    def set_x_offset(self, x_offset: float):
        """Scroll horizontally."""
        _padding = Config.timeline.horizontal_padding
        _max_offset = (self._sequence.get_duration()*self._x_zoom + 2*_padding
                       - self._view.viewport().width())
        self._x_offset = max(0, min(x_offset, _max_offset))

        # Update widgets:
        self._view.set_x_offset(self._x_offset)
        self._h_scroll_bar.setValue(self._x_offset)

    def set_x_zoom(self, x_zoom: float, relative: bool = False):
        """Zoom horizontally."""
        _padding = Config.timeline.horizontal_padding
        _duration = self._sequence.get_duration()
        _view_width = self._view.viewport().width()
        _min_zoom = (_view_width - 2*_padding) / _duration
        _max_zoom = Config.timeline.max_pixels_per_frame
        _zoom = x_zoom
        if relative:
            _zoom = _min_zoom + x_zoom*(_max_zoom-_min_zoom)
        self._x_zoom = max(_min_zoom, min(_zoom, _max_zoom))
        _max_offset = _duration*self._x_zoom + 2*_padding - _view_width
        if self._x_offset > _max_offset:
            self.set_x_offset(_max_offset)
        
        # Update widgets:
        self._view.set_x_zoom(self._x_zoom)
        self._h_scroll_bar.setRange(0, _max_offset)
        self._h_scroll_bar.setPageStep(_view_width)
        self._h_scroll_bar.setVisible(_max_offset > 0)
        self._zoom_slider.setValue(round(100*(self._x_zoom-_min_zoom)
                                         /(_max_zoom-_min_zoom)))
    
    def set_y_offset(self, y_offset: float):
        """Scroll vertically."""
        _max_offset = max(0, self._stack_height
                             - self._view.viewport().height()
                             + Config.timeline.ruler_height)
        self._y_offset = max(0, min(y_offset, _max_offset))

        # Update widgets:
        self._view.set_y_offset(self._y_offset)
        self._list.set_y_offset(self._y_offset)
        self._v_scroll_bar.setValue(self._y_offset)
    
    def set_stack_height(self, stack_height: float):
        """Update the layer stack total height."""
        self._stack_height = stack_height
        _max_offset = max(0, self._stack_height
                             - self._view.viewport().height()
                             + Config.timeline.ruler_height)
        if self._y_offset > _max_offset:
            self.set_y_offset(_max_offset)
        
        # Update widgets:
        self._v_scroll_bar.setRange(0, _max_offset)
        self._v_scroll_bar.setVisible(_max_offset > 0)
    
    def horiz_scroll_bar_moved(self, value: int):
        """Handle moving the horizontal scroll bar."""
        self.set_x_offset(value)
    
    def vert_scroll_bar_moved(self, value: int):
        """Handle moving the vertical scroll bar."""
        self.set_y_offset(value)
    
    def handle_view_resized(self):
        """Handle resizing the view."""
        self.set_x_zoom(self._x_zoom)
        self._v_scroll_bar.setPageStep(self._view.viewport().height()
                                       - Config.timeline.ruler_height)
        _max_offset = max(0, self._stack_height
                             - self._view.viewport().height()
                             + Config.timeline.ruler_height)
        self._v_scroll_bar.setRange(0, _max_offset)
        self._v_scroll_bar.setVisible(_max_offset > 0)
    
    def set_current_frame(self, frame: int):
        """Set the current frame."""
        _max_frame = self._sequence.get_duration()-1
        self._current_frame = max(0, min(frame, _max_frame))

        # Update widgets:
        self._view.set_current_frame(self._current_frame)

    def offset_current_frame(self, offset: int):
        """Offset the current frame."""
        self.set_current_frame(self._current_frame + offset)

    def update_sequence(self):
        """Handles updating the sequence."""
        self.set_x_zoom(self._x_zoom)
        self.set_x_offset(self._x_offset)
        self.set_y_offset(self._y_offset)
        self.set_current_frame(self._current_frame)
        self._view.update_scene_rect()
        self._view.update_layers()
        self._list.update_layers()
    
    def zoom_slider_moved(self, value: int):
        """Handle changes in the zoom slider."""
        _left_frame = self._view.mapToScene(QPoint(0, 0)).x()
        _right_frame = self._view.mapToScene(
            QPoint(self._view.viewport().width(), 0)).x()
        if (_left_frame <= self._current_frame
            and _right_frame > self._current_frame):
            _fixed_frame = self._current_frame
        else:
            _fixed_frame = (_left_frame + _right_frame)/2
        _fixed_pos = self._view.mapFromScene(QPointF(_fixed_frame, 0)).x()
        self.set_x_zoom(float(value)/100, True)
        _new_pos = self._view.mapFromScene(QPointF(_fixed_frame, 0)).x()
        _delta = _new_pos - _fixed_pos
        self.set_x_offset(self._x_offset + _delta)