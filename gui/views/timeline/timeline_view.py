"""
The visual timeline part of a TimelineTab.

The TimelineView inherits from QGraphicsView and provides
the user with a visual timeline within a TimelineTab.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QWidget)

from utils.config import Config
from utils.notification import Notification
from core.entities.sequence import Sequence
from core.entities.project import Project
from core.entities.layer import Layer
from gui.views.timeline.layer_rect import LayerRect


class TimelineView(QGraphicsView):
    """The visual timeline part of a TimelineTab."""

    _zoom: float  # zoom in pixels per frame
    _scene: QGraphicsScene
    _sequence: Sequence
    _layer_rect_list: list[LayerRect]

    middle_mouse_press_signal: Notification
    middle_mouse_release_signal: Notification
    mouse_move_signal: Notification
    page_step_changed_signal: Notification

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence = Project.get_sequence_dict()[sequence_id]
        self._layer_rect_list = []
        self._zoom = 1

        self.middle_mouse_press_signal = Notification()
        self.middle_mouse_release_signal = Notification()
        self.mouse_move_signal = Notification()
        self.page_step_changed_signal = Notification()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundBrush(QBrush(QColor(255,0,0)))
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        for i in range(20):
            _layer = Layer(f"Layer {i}", i*20, i*20+100)
            _layer_rect = LayerRect(_layer)
            self._scene.addItem(_layer_rect)
            self._layer_rect_list.append(_layer_rect)

    def resizeEvent(self, event: QResizeEvent):
        """Handle resizing the widget."""
        # TEMPORARY: zoom fits duration
        #_zoom = self.viewport().width() / self._sequence.get_duration()
        #self.change_zoom(_zoom)
        self.update_scene_dimensions()

    def change_zoom(self, zoom: float):
        """Change the horizontal zoom value."""
        _max_zoom = Config().timeline.max_pixels_per_frame
        self._zoom = min(_max_zoom, zoom)
        self.update_scene_dimensions()

    def update_scene_dimensions(self):
        """Adapt the scene dimensions to the viewport and zoom."""
        _viewport_width = self.viewport().width()
        _min_zoom = _viewport_width / self._sequence.get_duration()
        self._zoom = max(_min_zoom, self._zoom)
        _scene_width = self._sequence.get_duration() * self._zoom
        self._scene.setSceneRect(
            0, 0, _scene_width, self.viewport().height())
        _scrollbar = self.horizontalScrollBar()
        _scrollbar.setRange(0, _scene_width - _viewport_width)
        _page_step = max(1, _viewport_width)
        _scrollbar.setPageStep(_page_step)
        self.page_step_changed_signal.emit(_scrollbar.pageStep())
        self.update_layers()

    def update_layers(self):
        """Update the display of the layers."""
        _index = 0
        for _layer_rect in self._layer_rect_list:
            _start_frame, _end_frame = _layer_rect.get_frame_bounds()
            _x = _start_frame * self._zoom
            _y = (len(self._layer_rect_list)-1-_index)*(
                 Config().timeline.layer_height
                 + Config().timeline.layer_spacing)
            _width = (_end_frame - _start_frame) * self._zoom
            _height = Config().timeline.layer_height
            _layer_rect.setRect(_x, _y, _width, _height)
            _index += 1

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
