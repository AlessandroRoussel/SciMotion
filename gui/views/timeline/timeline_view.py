"""
The visual timeline part of a TimelineTab.

The TimelineView inherits from QGraphicsView and provides
the user with a visual timeline within a TimelineTab.
"""

import numpy as np
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF
from PySide6.QtGui import (QBrush, QTextItem, QResizeEvent, QMouseEvent,
                           QWheelEvent, QPainter, QPen, QPolygonF, QKeyEvent)
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QWidget)

from utils.config import Config
from utils.notification import Notification
from core.entities.sequence import Sequence
from gui.views.timeline.layer_rect import LayerRect
from gui.services.sequence_gui_service import SequenceGUIService
from utils.time import Time


class TimelineView(QGraphicsView):
    """The visual timeline part of a TimelineTab."""

    _sequence: Sequence
    _layer_rect_list: list[LayerRect]
    _middle_mouse_pressed: bool
    _dragging_cursor: bool
    _prev_mouse_pos: QPointF

    _x_offset: float
    _y_offset: float
    _x_zoom: float
    _stack_height: float
    _current_frame: int

    resize_signal: Notification
    x_zoom_signal: Notification
    x_offset_signal: Notification
    stack_height_signal: Notification
    y_offset_signal: Notification

    def __init__(self, parent: QWidget, sequence: Sequence):
        super().__init__(parent)

        self._sequence = sequence
        self._layer_rect_list = []
        self._dragging_cursor = False
        self._middle_mouse_pressed = False
        self._x_offset = 0
        self._y_offset = 0
        self._x_zoom = 1
        self._stack_height = 0
        self._current_frame = 0
        self.resize_signal = Notification()
        self.x_zoom_signal = Notification()
        self.x_offset_signal = Notification()
        self.stack_height_signal = Notification()
        self.y_offset_signal = Notification()

        _scene = QGraphicsScene()
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setScene(_scene)
        self.setStyleSheet("border: 0px")
        self.setMouseTracking(True)

    def build_layers(self):
        """Build the display of the layers."""
        self._layer_rect_list = []
        self.scene().clear()
        _index = 0
        self._stack_height = 0
        _spacing = Config.timeline.layer_spacing
        _layer_height = Config.timeline.layer_height
        _layer_list = self._sequence.get_layer_list()
        for _layer in _layer_list:
            _layer_rect = LayerRect(_layer)
            self._layer_rect_list.append(_layer_rect)
            self.scene().addItem(_layer_rect)
            _start_frame, _end_frame = _layer_rect.get_frame_bounds()
            _y = (len(_layer_list) - 1 - _index)*(_layer_height + _spacing)
            _width = _end_frame - _start_frame
            _layer_rect.setRect(_start_frame, _y, _width, _layer_height)
            self._stack_height += _layer_height + _spacing
            _index += 1
        self._stack_height = max(0, self._stack_height - _spacing)
        self.update_scene_rect()
        self.stack_height_signal.emit(self._stack_height)
    
    def update_scene_rect(self):
        """Update the scene area to match the duration and layer stack."""
        _width = self._sequence.get_duration()
        _height = max(self.viewport().height(), self._stack_height)
        _ruler_height = Config.timeline.ruler_height
        self.setSceneRect(0, -_ruler_height, _width, _height + _ruler_height)
        self.update_transform()

    def set_x_offset(self, x_offset: float):
        """Set the x offset value."""
        self._x_offset = x_offset
        self.update_transform()
    
    def set_y_offset(self, y_offset: float):
        """Set the y offset value."""
        self._y_offset = y_offset
        self.update_transform()
    
    def set_current_frame(self, frame: int):
        """Set the current frame value."""
        self._current_frame = frame
        self.update()
    
    def set_x_zoom(self, x_zoom: float):
        """Set the x zoom value."""
        self._x_zoom = x_zoom
        self.update_transform()
    
    def update_transform(self):
        """Update the transformation matrix."""
        self.resetTransform()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.scale(self._x_zoom, 1)
        self.translate(-self._x_offset/self._x_zoom, -self._y_offset)
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resizing the viewport."""
        super().resizeEvent(event)
        self.resize_signal.emit(event)
        self.update_scene_rect()
        _old_width = event.oldSize().width()
        _new_width = event.size().width()
        _old_center_frame = self.frame_at_position(QPointF(_old_width/2, 0))
        _new_center_frame = self.frame_at_position(QPointF(_new_width/2, 0))
        _x_delta = (_old_center_frame - _new_center_frame) * self._x_zoom
        self.x_offset_signal.emit(self._x_offset + _x_delta)

    def wheelEvent(self, event: QWheelEvent):
        """Override the wheel event."""
        _delta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            _factor = np.exp(_delta/100.*Config.timeline.zoom_sensitivity)
            _old_center_frame = self.frame_at_position(event.position())
            self.x_zoom_signal.emit(_factor * self._x_zoom)
            _new_center_frame = self.frame_at_position(event.position())
            _x_delta = (_old_center_frame - _new_center_frame) * self._x_zoom
            self.x_offset_signal.emit(self._x_offset + _x_delta)
            return
        _y_offset = self._y_offset-_delta*Config.timeline.scroll_sensitivity
        self.y_offset_signal.emit(_y_offset)
    
    def frame_at_position(self, position: QPointF) -> float:
        """Get the frame at a position."""
        return self.mapToScene(position.toPoint()).x()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if event.button() == Qt.MiddleButton:
            self._middle_mouse_pressed = True
            self._prev_mouse_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            return
        if (event.button() == Qt.LeftButton
            and event.position().y() < Config.timeline.ruler_height):
            self._dragging_cursor = True
            _mouse_pos = event.position()
            _frame = np.round(self.mapToScene(_mouse_pos.toPoint()).x())
            SequenceGUIService.set_current_frame(_frame)
            self.setCursor(Qt.SizeHorCursor)
            return

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle the mouse move event."""
        if self._middle_mouse_pressed:
            _mouse_pos = event.position()
            _delta = _mouse_pos - self._prev_mouse_pos
            self.x_offset_signal.emit(self._x_offset - _delta.x())
            self.y_offset_signal.emit(self._y_offset - _delta.y())
            self._prev_mouse_pos = _mouse_pos

        if self._dragging_cursor:
            _mouse_pos = event.position()
            _frame = np.round(self.mapToScene(_mouse_pos.toPoint()).x())
            SequenceGUIService.set_current_frame(_frame)
        
        if event.buttons() == Qt.NoButton:
            _mouse_pos = event.position()
            _current_frame_x = self.mapFromScene(
                QPointF(self._current_frame, 0)).x()
            if (_mouse_pos.y() < Config.timeline.ruler_height
                and (abs(_mouse_pos.x() - _current_frame_x)
                     < Config.timeline.cursor_handle_width/2)):
                    self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)


    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self._middle_mouse_pressed = False
            self.setCursor(Qt.ArrowCursor)
            return
        if (self._dragging_cursor and event.button() == Qt.LeftButton):
            self._dragging_cursor = False
            self.setCursor(Qt.ArrowCursor)
            return

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key_Left:
            SequenceGUIService.offset_current_frame(-1)
            return
        if event.key() == Qt.Key_Right:
            SequenceGUIService.offset_current_frame(1)
            return

    def drawBackground(self, qp: QPainter, rect: QRectF):
        """Draw the background grid and visuals."""
        _fps = self._sequence.get_frame_rate()
        _layer_height = Config.timeline.layer_height
        _layer_spacing = Config.timeline.layer_spacing
        _layer_block_height = _layer_height + _layer_spacing
        _min_frame = np.floor(rect.x()).astype(int)
        _max_frame = np.ceil(rect.x()+rect.width()).astype(int)
        _y_min = rect.y()
        _y_max = rect.y() + rect.height()
        _rect_width = rect.width()

        # Draw horizontal alternating blocks:
        _color = self.palette().text().color()
        _color.setAlpha(10)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)
        _start_index = 2*np.floor(_y_min/2/_layer_block_height).astype(int)
        _end_index = np.ceil(_y_max/_layer_block_height).astype(int)
        for _index in range(_start_index, _end_index, 2):
            _y = _index*_layer_block_height
            qp.drawRect(rect.x()-1, _y, _rect_width+2, _layer_block_height)

        # Draw vertical alternating blocks:
        _frame_spacing = self.viewport().width() / _rect_width
        _min_spacing = Config.timeline.time_grid_min_spacing
        _rate = 1
        _rate_ratios = [_fps, 60, 60]
        for _rate_ratio in _rate_ratios:
            if _frame_spacing*_rate > _min_spacing:
                _min_subdiv = 2*np.floor(_min_frame/2/_rate).astype(int)
                _max_subdiv = np.ceil(_max_frame/_rate).astype(int)
                for _subdiv in range(_min_subdiv, _max_subdiv, 2):
                    _frame = float(_subdiv)*_rate
                    qp.drawRect(_frame, _y_min, _rate, rect.height())
                break
            _rate *= _rate_ratio

    def drawForeground(self, qp: QPainter, rect: QRectF):
        """Draw the foreground ruler and elements."""
        # Ruler background:
        _ruler_height = Config.timeline.ruler_height
        qp.setPen(Qt.NoPen)
        qp.setBrush(QBrush(self.palette().window().color()))
        _ruler = QRectF(rect.x(), rect.y(), rect.width(), _ruler_height)
        qp.drawRect(_ruler)

        # Ruler border:
        _color = self.palette().text().color()
        _pen = QPen(_color)
        _pen.setCosmetic(True)
        _pen.setWidth(1)
        qp.setPen(_pen)
        _ruler_border = QLineF(rect.x(), rect.y()+_ruler_height,
                               rect.x()+rect.width(), rect.y()+_ruler_height)
        qp.drawLine(_ruler_border)

        # Ruler texts:
        qp.save()
        qp.scale(1/self._x_zoom, 1)
        qp.setPen(QPen(self.palette().text().color()))
        _fps = self._sequence.get_frame_rate()
        _min_frame = np.floor(rect.x()).astype(int)
        _max_frame = np.ceil(rect.x()+rect.width()).astype(int)
        _frame_spacing = self.viewport().width() / rect.width()
        _min_spacing = Config.timeline.time_grid_min_spacing
        _text_min_spacing = Config.timeline.time_text_min_spacing
        _rate = 1
        _rate_ratios = [_fps, 60, 60]
        for _rate_ratio in _rate_ratios:
            if _frame_spacing*_rate > _min_spacing:
                _min_subdiv = _rate_ratio*np.floor(
                                _min_frame/_rate/_rate_ratio)
                _max_subdiv = np.ceil(_max_frame/_rate).astype(int)
                _step = np.ceil(_text_min_spacing
                                /_frame_spacing/_rate).astype(int)
                _subdiv = _min_subdiv
                _steps = 0
                while _subdiv < _max_subdiv:
                    _frame = _subdiv*_rate
                    _text = Time.format_time(_frame, _fps, short=True)
                    qp.drawText(
                        _frame*self._x_zoom-_text_min_spacing/2,rect.y(),
                        _text_min_spacing, _ruler_height,
                        Qt.AlignmentFlag.AlignCenter, _text)
                    _steps += _step
                    if _steps >= _rate_ratio or _steps + _step > _rate_ratio:
                        _subdiv = _rate_ratio*np.ceil(_subdiv/_rate_ratio)
                        _steps = 0
                    else:
                        _subdiv += float(_step)
                break
            _rate *= _rate_ratio
        qp.restore()

        # Cursor:
        _pen = QPen(self.palette().text().color())
        _pen.setCosmetic(True)
        _pen.setWidthF(1.5)
        qp.setPen(_pen)
        _ruler_border = QLineF(self._current_frame, rect.y(),
                               self._current_frame, rect.y()+rect.height())
        qp.drawLine(_ruler_border)

        qp.setBrush(QBrush(self.palette().text().color()))
        _triangle_width = Config.timeline.cursor_handle_width/self._x_zoom
        _triangle = QPolygonF([
            QPointF(self._current_frame-_triangle_width/2, rect.y()),
            QPointF(self._current_frame, rect.y()+_ruler_height),
            QPointF(self._current_frame+_triangle_width/2, rect.y())])
        qp.drawPolygon(_triangle)

        # Cursor frame:
        _color = self.palette().text().color()
        _color.setAlpha(50)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)
        qp.drawRect(self._current_frame, rect.y()+_ruler_height,
                    1, rect.height())
