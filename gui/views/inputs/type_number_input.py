"""An input for entering a Number only by typing."""

from typing import Union

from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
from PySide6.QtCore import Qt, QTimer

from data_types.number import Number
from utils.notification import Notification
from utils.config import Config


class TypeNumberInput(QLineEdit):
    """An input for entering a Number only by typing."""

    _value: float
    _min: float
    _max: float

    _decimals: int
    _display_factor: float

    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Number, float] = None,
                 min: Union[Number, float] = Number.negInfinity,
                 max: Union[Number, float] = Number.Infinity,
                 decimals: int = 6,
                 color: list[int] = None,
                 display_factor: float = 1):
        super().__init__(parent)
        if value is not None and not isinstance(value, Number):
            value = Number(value)
        if min is not None and not isinstance(min, Number):
            min = Number(min)
        if max is not None and not isinstance(max, Number):
            max = Number(max)

        self._min = min.get_value()
        self._max = max.get_value()
        self._decimals = decimals
        self._display_factor = display_factor

        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        if color is None:
            _color = QApplication.palette().accent().color()
            _rgb = (f"rgb({_color.red()}, {_color.green()}, {_color.blue()})")
        else:
            _rgb = (f"rgb({color[0]}, {color[1]}, {color[2]})")
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
        self.set_value((value.get_value() if value is not None
                         else Number.default().get_value()))
        self._update_width()
    
    def block_signals(self, block: bool = True):
        """Block / unblock signals."""
        self.value_changed.block(block)

    def set_value(self, value: float):
        """Set the value stored by the input."""
        self._value = min(max(value, self._min), self._max)
        self.value_changed.emit(self.get_value())
        self._update_text()
    
    def _update_text(self):
        """Update the text to match the value."""
        _val = self._value*self._display_factor
        self.setText(f"{_val:.{self._decimals}f}")
    
    def keyPressEvent(self, event):
        """Handle key press event."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        super().keyPressEvent(event)
    
    def focusInEvent(self, event):
        """Handle focus in event."""
        self.setCursor(Qt.IBeamCursor)
        QTimer.singleShot(0, self.selectAll)
    
    def focusOutEvent(self, event):
        """Handle focus out event."""
        self.setCursor(Qt.PointingHandCursor)
        try:
            self.set_value(float(self.text())/self._display_factor)
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