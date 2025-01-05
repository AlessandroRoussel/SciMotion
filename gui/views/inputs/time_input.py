"""An input for entering a Time."""

from typing import Union

from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

from data_types.integer import Integer
from utils.notification import Notification
from utils.time import Time
from utils.config import Config


class TimeInput(QLineEdit):
    """An input for entering a Time."""

    _value: float
    _min: int
    _max: int
    _frame_rate: float

    _last_mouse_pos: QPoint
    _start_value: int
    _step: float

    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Integer, int] = None,
                 frame_rate: float = 60,
                 min: Union[Integer, int] = None,
                 max: Union[Integer, int] = None,
                 step: float = 1):
        super().__init__(parent)
        if value is not None and not isinstance(value, Integer):
            value = Integer(value)
        if min is not None and not isinstance(min, Integer):
            min = Integer(min)
        if max is not None and not isinstance(max, Integer):
            max = Integer(max)

        self._last_mouse_pos = None
        self._min = min.get_value() if min is not None else None
        self._max = max.get_value() if max is not None else None
        self._frame_rate = frame_rate
        self._step = step
        self._value = None

        self.setAlignment(Qt.AlignCenter)
        self.setFocusPolicy(Qt.TabFocus)
        self.setCursor(Qt.SizeHorCursor)

        _color = QApplication.palette().accent().color()
        _rgb = (f"rgb({_color.red()}, {_color.green()}, {_color.blue()})")
        self.setStyleSheet(f"""
            QLineEdit {{
                padding: {Config.input.padding};
                border-radius: 0;
                background-color: transparent;
                border: 1px solid transparent;
                color: {_rgb};
            }}
            QLineEdit:hover {{
                border-bottom: 1px solid {_rgb};
            }}
            QLineEdit:focus {{
                border-radius: 3px;
                border: 1px solid {_rgb};
            }}
            """)
        
        self.value_changed = Notification()
        self.textChanged.connect(self._update_width)
        self._set_value((value.get_value() if value is not None
                         else Integer.default().get_value()))
        self._update_width()
    
    def _set_value(self, value: Union[float, int]):
        """Set the value stored by the input."""
        _prev_value = self._value
        if self._min is not None and self._max is not None:
            self._value = min(max(value, self._min), self._max)
        elif self._min is not None:
            self._value = max(value, self._min)
        elif self._max is not None:
            self._value = min(value, self._max)
        else:
            self._value = value
        if(_prev_value is None
           or int(round(_prev_value)) != int(round(self._value))):
            self.value_changed.emit(self.get_value())
        self._update_text()
    
    def _update_text(self):
        """Update the text to match the value."""
        self.setText(Time.format_time(self._value, self._frame_rate))
    
    def change_frame_rate(self, frame_rate: float):
        """Change the input's local frame rate."""
        _new_val = self._value / self._frame_rate * frame_rate
        self._frame_rate = frame_rate
        self._set_value(_new_val)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            if not self.hasFocus():
                self._last_mouse_pos = event.globalPosition().toPoint()
                self.setFocus()
                self.clearFocus()
                self._start_value = self._value
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move event."""
        if self._last_mouse_pos is not None:
            _delta = event.globalPosition().toPoint() - self._last_mouse_pos
            _speed = 1
            if event.modifiers() & Qt.ControlModifier:
                _speed = .1
            elif event.modifiers() & Qt.ShiftModifier:
                _speed = 10
            self._set_value(self._value + _delta.x() * self._step * _speed)
            self._last_mouse_pos = event.globalPosition().toPoint()
            self.clearFocus()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release event."""
        if event.button() == Qt.LeftButton:
            if not self.hasFocus():
                self._last_mouse_pos = None
                if self._start_value == self._value:
                    self.setFocus()
                    self.setCursor(Qt.IBeamCursor)
                    self.selectAll()
            else:
                super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press event."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus out event."""
        self.setCursor(Qt.SizeHorCursor)
        _text = self.text()
        if Time.is_duration(_text):
            _value = Time.duration_from_str(_text, self._frame_rate)
            self._set_value(_value)
        else:
            self._update_text()
        super().focusOutEvent(event)
    
    def _update_width(self):
        """Update width to match content."""
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        self.setFixedWidth(text_width + 12)
    
    def get_value(self) -> int:
        """Return the value."""
        return int(round(self._value))