"""An input for entering a Number."""

from typing import Union

from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

from data_types.number import Number
from utils.notification import Notification
from utils.config import Config


class NumberInput(QLineEdit):
    """An input for entering a Number."""

    _value: float
    _min: float
    _max: float
    _decimals: int

    _last_mouse_pos: QPoint
    _start_value: float
    _step: float

    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Number, float] = None,
                 min: Union[Number, float] = None,
                 max: Union[Number, float] = None,
                 decimals: int = 6,
                 step: float = .1):
        super().__init__(parent)
        if value is not None and not isinstance(value, Number):
            value = Number(value)
        if min is not None and not isinstance(min, Number):
            min = Number(min)
        if max is not None and not isinstance(max, Number):
            max = Number(max)

        self._last_mouse_pos = None
        self._min = min.get_value() if min is not None else None
        self._max = max.get_value() if max is not None else None
        self._decimals = decimals
        self._step = step

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
                         else Number.default().get_value()))
        self._update_width()
    
    def _set_value(self, value: float):
        """Set the value stored by the input."""
        if self._min is not None and self._max is not None:
            self._value = min(max(value, self._min), self._max)
        elif self._min is not None:
            self._value = max(value, self._min)
        elif self._max is not None:
            self._value = min(value, self._max)
        else:
            self._value = value
        self.value_changed.emit(self.get_value())
        self._update_text()
    
    def _update_text(self):
        """Update the text to match the value."""
        self.setText(f"{self._value:.{self._decimals}f}")

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
        try:
            self._set_value(float(self.text()))
        except ValueError:
            self._update_text()
        super().focusOutEvent(event)
    
    def _update_width(self):
        """Update width to match content."""
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        self.setFixedWidth(text_width + 12)
    
    def get_value(self) -> Number:
        """Return the value."""
        return Number(self._value)
    
    def get_float_value(self) -> float:
        """Return the value."""
        return self._value