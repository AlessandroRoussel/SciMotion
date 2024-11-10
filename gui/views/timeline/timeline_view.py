"""
The visual timeline part of a TimelineTab.

The TimelineView inherits from QGraphicsView and provides
the user with a visual timeline within a TimelineTab.
"""

import numpy as np
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, QPoint, QTimer
from PySide6.QtGui import (QBrush, QColor, QResizeEvent, QMouseEvent,
                           QWheelEvent, QPainter, QPen, QPolygonF,
                           QKeyEvent, QFontMetrics)
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QWidget)

from utils.config import Config
from utils.notification import Notification
from core.entities.sequence import Sequence
from gui.views.timeline.layer_rect import LayerRect
from gui.services.sequence_gui_service import SequenceGUIService
from core.services.project_service import ProjectService
from utils.time import Time


class TimelineView(QGraphicsView):
    """The visual timeline part of a TimelineTab."""

    _sequence_id: int
    _sequence: Sequence
    _layer_rect_list: list[LayerRect]
    _selected_layer_rects: set[LayerRect]
    _middle_mouse_pressed: bool
    _dragging_cursor: bool
    _prev_mouse_pos: QPointF
    _h_scroll_timer: QTimer
    _h_scroll_direction: int
    _h_scroll_position: QPointF

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

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)

        self._sequence_id = sequence_id
        self._sequence = ProjectService.get_sequence_by_id(sequence_id)
        self._layer_rect_list = []
        self._selected_layer_rects = set()
        self._dragging_cursor = False
        self._middle_mouse_pressed = False
        self._h_scroll_timer = QTimer()
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
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)
        self.setFocusPolicy(Qt.WheelFocus)

        self._h_scroll_timer.timeout.connect(self.overshoot_scroll)
    
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
            _layer_rect = LayerRect(_layer, self._sequence_id)
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
    
    def update_transform(self):
        """Update the transformation matrix."""
        self.resetTransform()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.scale(self._x_zoom, 1)
        _padding = Config.timeline.horizontal_padding
        _ruler_height = Config.timeline.ruler_height
        self.centerOn(-_padding/self._x_zoom, -_ruler_height)
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
        
        super().mousePressEvent(event)

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
                _left_frame = self.mapToScene(QPoint(0, 0)).x()
                _right_frame = self.mapToScene(
                    QPoint(self.viewport().width(), 0)).x()
                if _frame < _left_frame:
                    self._h_scroll_direction = -1
                    self._h_scroll_position = event.position()
                    if not self._h_scroll_timer.isActive():
                        self._h_scroll_timer.start(
                            Config.timeline.overshoot_drag_interval)
                elif _frame > _right_frame:
                    self._h_scroll_direction = 1
                    self._h_scroll_position = event.position()
                    if not self._h_scroll_timer.isActive():
                        self._h_scroll_timer.start(
                            Config.timeline.overshoot_drag_interval)
                else:
                    self._h_scroll_direction = 0
                    self._h_scroll_timer.stop()
        
        if event.buttons() == Qt.NoButton:
            _mouse_pos = event.position()
            _current_frame_x = self.mapFromScene(
                QPointF(self._current_frame, 0)).x()
            _ruler_height = Config.timeline.ruler_height
            _min_cursor_y = _ruler_height-Config.timeline.cursor_handle_height
            if (_mouse_pos.y() < _ruler_height
                and _mouse_pos.y() >= _min_cursor_y
                and (abs(_mouse_pos.x() - _current_frame_x)
                     <= Config.timeline.cursor_handle_width/2)):
                    self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        super().mouseMoveEvent(event)

    def overshoot_scroll(self):
        """Scroll the view if the cursor overshoots the view."""
        if self._dragging_cursor:
            _mouse_pos = self._h_scroll_position
            _frame = np.round(self.mapToScene(_mouse_pos.toPoint()).x())
            SequenceGUIService.set_current_frame(_frame)
            _drag_speed = Config.timeline.overshoot_drag_speed
            _interval = Config.timeline.overshoot_drag_interval
            if self._h_scroll_direction < 0:
                _distance = abs(_mouse_pos.x())
            else:
                _distance = abs(_mouse_pos.x()-self.viewport().width())
            _drag_speed *= _distance*_interval/1000
            self.x_offset_signal.emit(
                self._x_offset + _drag_speed*self._h_scroll_direction)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self._middle_mouse_pressed = False
            self.setCursor(Qt.ArrowCursor)
            return
        if (self._dragging_cursor and event.button() == Qt.LeftButton):
            self._dragging_cursor = False
            self._h_scroll_direction = 0
            self._h_scroll_timer.stop()
            self.setCursor(Qt.ArrowCursor)
            return
        super().mouseReleaseEvent(event)

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
                if _rate < _rect_width or _rate == 1:
                    _min_div = 2*np.floor(_min_frame/2/_rate).astype(int)
                    _max_div = np.ceil(_max_frame/_rate).astype(int)
                    for _div in range(_min_div, _max_div, 2):
                        _frame = float(_div)*_rate
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

        _color = self.palette().text().color()
        _pen = QPen(_color)
        _pen.setCosmetic(True)
        _pen.setWidth(1)

        _color.setAlphaF(.3)
        _pen_translucent = QPen(_color)
        _pen_translucent.setCosmetic(True)
        _pen_translucent.setWidth(1)

        _font = qp.font()
        _font.setPixelSize(Config.timeline.time_text_size)
        _font_metrics = QFontMetrics(_font)
        qp.setFont(_font)

        _fps = self._sequence.get_frame_rate()
        _min_frame = max(0, np.floor(rect.x()).astype(int))
        _max_frame = min(np.ceil(rect.x()+rect.width()).astype(int),
                         self._sequence.get_duration())
        _text_padding = Config.timeline.time_text_padding
        _duration_str = Time.format_time(self._sequence.get_duration(), _fps)
        _text_width = (_font_metrics.horizontalAdvance(_duration_str)
                           + _text_padding)
        _text_height = _font_metrics.height()

        _rates = [1, _fps, _fps*60, _fps*3600, _fps*3600]
        _sub_div_nums = [1, _fps, 60, 60, 1]
        for _i in range(len(_rates)):
            _rate =_rates[_i]
            _sub_divs = _sub_div_nums[_i]
            if _i == len(_rates)-1:
                _power = int(np.ceil(np.log2(_text_width
                                             /_rate/self._x_zoom)))
                _rate *= 2**_power
                _sub_div_nums *= 2**_power
            if _rate*self._x_zoom >= _text_width:
                _min_div = np.floor(_min_frame/_rate)
                _max_div = np.ceil(_max_frame/_rate)
                _sub_step_size = int(np.ceil(
                    _sub_divs*_text_width/self._x_zoom/_rate))
                _sub_steps = max(1, int(_sub_divs/_sub_step_size))
                for _div in range(int(_min_div), int(_max_div)+1):
                    for _sub_step in range(_sub_steps):
                        _sub_div = _sub_step * _sub_step_size
                        _frame = (_div + _sub_div/_sub_divs) * _rate
                        _text = Time.format_time(_frame, _fps, short=True)
                        if _sub_step == 0:
                            qp.setPen(_pen)
                            qp.drawLine(
                                _frame*self._x_zoom, rect.y(),
                                _frame*self._x_zoom, rect.y()+_ruler_height)
                            qp.drawText(QRectF(
                                _frame*self._x_zoom+_text_padding,
                                rect.y()+_ruler_height-_text_height,
                                _text_width,
                                _text_height),
                                Qt.AlignLeft,
                                _text)
                        else:
                            qp.setPen(_pen_translucent)
                            qp.drawLine(
                                _frame*self._x_zoom,
                                rect.y()+_ruler_height-_text_height,
                                _frame*self._x_zoom,
                                rect.y()+_ruler_height)
                            qp.drawText(QRectF(
                                _frame*self._x_zoom+_text_padding,
                                rect.y()+_ruler_height-_text_height,
                                _text_width,
                                _text_height),
                                Qt.AlignLeft,
                                _text)
                break

        qp.restore()

        # Cursor:
        _pen = QPen(self.palette().accent().color())
        _pen.setCosmetic(True)
        _pen.setWidthF(1.5)
        qp.setPen(_pen)
        _ruler_border = QLineF(self._current_frame, rect.y()+_ruler_height,
                               self._current_frame, rect.y()+rect.height())
        qp.drawLine(_ruler_border)

        qp.setBrush(QBrush(self.palette().accent().color()))
        _triangle_width = Config.timeline.cursor_handle_width/self._x_zoom
        _cursor_height = Config.timeline.cursor_handle_height
        _triangle_height = _cursor_height/3
        _rect_height = _cursor_height - _triangle_height
        _start_y = rect.y()+_ruler_height-_triangle_height
        _triangle = QPolygonF([
            QPointF(self._current_frame-_triangle_width/2, _start_y),
            QPointF(self._current_frame, _start_y+_triangle_height),
            QPointF(self._current_frame+_triangle_width/2, _start_y)])
        qp.drawPolygon(_triangle)
        qp.drawRect(QRectF(self._current_frame-_triangle_width/2,
                           _start_y-_rect_height,
                           _triangle_width,
                           _rect_height))

        # Cursor frame:
        _color = self.palette().accent().color()
        _color.setAlphaF(.1)
        _brush = QBrush(_color)
        qp.setBrush(_brush)
        qp.setPen(Qt.NoPen)
        qp.drawRect(self._current_frame, rect.y()+_ruler_height,
                    1, rect.height())

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key_Left:
            SequenceGUIService.offset_current_frame(-1)
            return
        if event.key() == Qt.Key_Right:
            SequenceGUIService.offset_current_frame(1)
            return
        if event.key() == Qt.Key_F:
            self.x_zoom_signal.emit(0)
            return
