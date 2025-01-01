"""An input for entering text."""

from typing import Union

from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

from data_types.number import Number
from utils.notification import Notification
from utils.config import Config


class TextInput(QLineEdit):
    """An input for entering text."""

    _value: str
    _not_empty: bool
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: str = "",
                 not_empty: bool = False):
        super().__init__(parent)
        self._not_empty = not_empty
        if not_empty and value=="":
            value = "Null"

        self.setAlignment(Qt.AlignLeft)
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
        self._set_value(value)
    
    def _set_value(self, value: str):
        """Set the value stored by the input."""
        if not self._not_empty or value.strip() != "":
            self._value = value.strip()
            self.value_changed.emit(self.get_value())
        self._update_text()
    
    def _update_text(self):
        """Update the text to match the value."""
        self.setText(self._value)
    
    def keyPressEvent(self, event):
        """Handle key press event."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus out event."""
        self._set_value(self.text())
        super().focusOutEvent(event)
    
    def get_value(self) -> str:
        """Return the value."""
        return self._value
