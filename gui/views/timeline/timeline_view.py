"""
The visual timeline part of a TimelineTab.

The TimelineView inherits from QGraphicsView and provides
the user with a visual timeline within a TimelineTab.
"""

import numpy as np
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF
from PySide6.QtGui import (QBrush, QColor, QResizeEvent, QMouseEvent,
                           QWheelEvent, QPainter, QPen, QPolygonF,
                           QKeyEvent)
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
    _selected_layer_rects: set[LayerRect]
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
        self._selected_layer_rects = set()
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
        _scene.setStickyFocus(False)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setScene(_scene)
        self.setStyleSheet("border: 0px")
        self.setMouseTracking(True)

        self.setFocusPolicy(Qt.WheelFocus)
    
    def update_layers(self):
        """Update the display of the layers."""
        # TODO : not destroy all layers and rebuild
        self._layer_rect_list = []
        self._selected_layer_rects = set()
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
            _layer_rect.set_rect(_start_frame, _y, _width, _layer_height)
            self._stack_height += _layer_height + _spacing
            _index += 1
        self._stack_height = max(0, self._stack_height - _spacing)
        self.update_scene_rect()
        self.stack_height_signal.emit(self._stack_height)

    def select_layer(self, layer_rect: LayerRect):
        """Handle selecting a layer."""
        print(layer_rect)

    def update_scene_rect(self):
        """Update the scene area to match the duration and layer stack."""
        _padding = Config.timeline.horizontal_padding
        _width = self._sequence.get_duration() + 2*_padding/self._x_zoom
        _height = max(self.viewport().height(), self._stack_height)
        _ruler_height = Config.timeline.ruler_height
        self.setSceneRect(-_padding/self._x_zoom, -_ruler_height,
                          _width, _height + _ruler_height)
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
        self.update_scene_rect()
        self.update_transform()
    
    def update_transform(self):
        """Update the transformation matrix."""
        self.resetTransform()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.scale(self._x_zoom, 1)
        self.translate(-self._x_offset/self._x_zoom,
                       -self._y_offset)
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resizing the viewport."""
        super().resizeEvent(event)
        self.resize_signal.emit()
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
            self.update()
            return
        
        if event.button() == Qt.LeftButton:
            _item = self.itemAt(event.pos())
            if event.modifiers() != Qt.ControlModifier:
                if len(self._selected_layer_rects) > 0:
                    for _selected_rect in self._selected_layer_rects:
                        _selected_rect.deselect()
                    self._selected_layer_rects = set()
            if _item is None or not isinstance(_item, LayerRect):
                self.update()
                return
            self._selected_layer_rects.add(_item)
            _item.select()
            self.update()

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
            if event.modifiers() == Qt.ShiftModifier:
                if len(self._layer_rect_list) > 0:
                    _mouse_frame = self.mapToScene(_mouse_pos.toPoint()).x()
                    _distance = float("inf")
                    _frame = 0
                    for _layer_rect in self._layer_rect_list:
                        for _frm in _layer_rect.get_frame_bounds():
                            if abs(_frm - _mouse_frame) < _distance:
                                _distance = abs(_frm - _mouse_frame)
                                _frame = _frm
                                if _distance == 0:
                                    break
                    SequenceGUIService.set_current_frame(_frame)
            else:
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

    def draw_stripes(self, qp: QPainter, rect: QRectF):
        """Draw the horizontal and vertical stripes."""
        _fps = self._sequence.get_frame_rate()
        _layer_height = Config.timeline.layer_height
        _layer_spacing = Config.timeline.layer_spacing
        _layer_block_height = _layer_height + _layer_spacing
        _min_frame = max(0, np.floor(rect.x()).astype(int))
        _max_frame = min(np.ceil(rect.x()+rect.width()).astype(int),
                         self._sequence.get_duration()-1)
        _y_min = rect.y()
        _y_max = rect.y() + rect.height()
        _rect_width = rect.width()

        # Draw horizontal alternating blocks:
        _color = self.palette().text().color()
        _color.setAlphaF(.02)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)

        if Config.timeline.horizontal_stripes:
            _start_index = 2*np.floor(_y_min/2/_layer_block_height).astype(int)
            _end_index = np.ceil(_y_max/_layer_block_height).astype(int)
            for _index in range(_start_index, _end_index, 2):
                _y = _index*_layer_block_height
                qp.drawRect(rect.x()-1, _y, _rect_width+2, _layer_block_height)

        # Draw vertical alternating blocks:
        if Config.timeline.vertical_stripes:
            _rates = [_fps*3600, _fps*60, _fps, 1]
            for _rate in _rates:
                if _rate < _rect_width:
                    _min_subdiv = 2*np.floor(_min_frame/2/_rate).astype(int)
                    _max_subdiv = np.ceil(_max_frame/_rate).astype(int)
                    for _subdiv in range(_min_subdiv, _max_subdiv, 2):
                        _frame = float(_subdiv)*_rate
                        qp.drawRect(_frame, _y_min, _rate, rect.height())
                    break

    def drawForeground(self, qp: QPainter, rect: QRectF):
        """Draw the foreground ruler and elements."""
        self.draw_stripes(qp, rect)

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

        # Draw out of range blocks:
        _color = QColor("black")
        _color.setAlphaF(.25)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)
        _padding = Config.timeline.horizontal_padding
        _width = np.ceil(_padding / self._x_zoom).astype(int)
        qp.drawRect(-_width, -_ruler_height,
                    _width, rect.height())
        qp.drawRect(self._sequence.get_duration(), -_ruler_height,
                    _width, rect.height())

        # Ruler texts:
        qp.save()
        qp.scale(1/self._x_zoom, 1)
        qp.setPen(QPen(self.palette().text().color()))
        _fps = self._sequence.get_frame_rate()
        _min_frame = max(0, np.floor(rect.x()).astype(int))
        _max_frame = min(np.ceil(rect.x()+rect.width()).astype(int),
                         self._sequence.get_duration())
        _grid_max_width = Config.timeline.time_grid_max_width
        _text_max_width = Config.timeline.time_text_max_width
        _rates = [_fps*3600, _fps*60, _fps, 1]
        _ratios = [1, 60, 60, _fps]
        for _rate, _sub_per_div in zip(_rates, _ratios):
            if _rate*self._x_zoom < _grid_max_width:
                _min_div = np.floor(_min_frame/_rate/_sub_per_div)
                _max_div = np.ceil(_max_frame/_rate/_sub_per_div)
                _step_size = int(np.ceil(_text_max_width/self._x_zoom/_rate))
                _steps = int(_sub_per_div/_step_size)
                for _div in range(int(_min_div), int(_max_div)):
                    for _step in range(_steps):
                        _subdiv = _step * _step_size
                        _frame = (_div*_sub_per_div + _subdiv)*_rate
                        _text = Time.format_time(_frame, _fps, short=True)
                        qp.drawText(
                            _frame*self._x_zoom-_text_max_width/2,rect.y(),
                            _text_max_width, _ruler_height,
                            Qt.AlignmentFlag.AlignCenter, _text)
                break
        qp.restore()

        # Cursor:
        _pen = QPen(self.palette().accent().color())
        _pen.setCosmetic(True)
        _pen.setWidthF(1.5)
        qp.setPen(_pen)
        _ruler_border = QLineF(self._current_frame, rect.y(),
                               self._current_frame, rect.y()+rect.height())
        qp.drawLine(_ruler_border)

        qp.setBrush(QBrush(self.palette().accent().color()))
        _triangle_width = Config.timeline.cursor_handle_width/self._x_zoom
        _triangle = QPolygonF([
            QPointF(self._current_frame-_triangle_width/2, rect.y()),
            QPointF(self._current_frame, rect.y()+_ruler_height),
            QPointF(self._current_frame+_triangle_width/2, rect.y())])
        qp.drawPolygon(_triangle)

        # Cursor frame:
        _color = self.palette().accent().color()
        _color.setAlphaF(.1)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)
        qp.drawRect(self._current_frame, rect.y()+_ruler_height,
                    1, rect.height())
