from typing import Union

from PySide6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

from data_types.integer import Integer
from utils.notification import Notification


class IntegerInput(QLineEdit):
    """An input for entering an Integer."""

    _value: float
    _min: int
    _max: int

    _last_mouse_pos: QPoint
    _start_value: int
    _step: float

    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Integer, float] = None,
                 min: Union[Integer, float] = Integer.Minimum,
                 max: Union[Integer, float] = Integer.Maximum,
                 step: float = .1):
        super().__init__(parent)
        if value is not None and not isinstance(value, Integer):
            value = Integer(value)
        if min is not None and not isinstance(min, Integer):
            min = Integer(min)
        if max is not None and not isinstance(max, Integer):
            max = Integer(max)

        self._last_mouse_pos = None
        self._min = min.get_value()
        self._max = max.get_value()
        self._step = step
        self._value = None

        self.setAlignment(Qt.AlignCenter)
        self.setFocusPolicy(Qt.TabFocus)
        self.setCursor(Qt.SizeHorCursor)

        _color = QApplication.palette().accent().color()
        _rgb = (f"rgb({_color.red()}, {_color.green()}, {_color.blue()})")
        self.setStyleSheet(f"""
            QLineEdit {{
                padding: 2px;
                border-radius: 0;
                border: none;
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 0;
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
        self._value = min(max(value, self._min), self._max)
        if(_prev_value is None
           or int(round(_prev_value)) != int(round(self._value))):
            self.value_changed.emit()
            self._update_text()
    
    def _update_text(self):
        """Update the text to match the value."""
        self.setText(f"{int(round(self._value))}")

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
            _slowing = 10 if event.modifiers() & Qt.ControlModifier else 1
            self._set_value(self._value + _delta.x() * self._step / _slowing)
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
                    self.selectAll()
                    self.setFocus()
                    self.setCursor(Qt.IBeamCursor)
            else:
                super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press event."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        else:
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
    
    def get_value(self) -> Integer:
        """Return the value."""
        return Integer(int(round(self._value)))
    
    def get_int_value(self) -> int:
        """Return the value."""
        return int(round(self._value))



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        _layout = QVBoxLayout(self)
        self._input = IntegerInput(self, 0, step=.1)
        self._input2 = IntegerInput(self, 10, min=4, max=15, step=.01)
        _layout.addWidget(self._input)
        _layout.addWidget(self._input2)
        self.setLayout(_layout)


if __name__ == "__main__":
    _app = QApplication([])
    _window = MainWindow()
    _window.show()
    _app.exec()