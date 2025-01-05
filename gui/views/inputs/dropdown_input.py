"""An input for choosing an option with a dropdown menu."""

from typing import Union

from PySide6.QtWidgets import QApplication, QComboBox, QWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

from data_types.integer import Integer
from utils.notification import Notification
from utils.config import Config


class DropdownInput(QComboBox):
    """An input for choosing an option with a dropdown menu."""

    _value: int
    _options: list[str]

    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Integer, int] = None,
                 options: list[str] = []):
        super().__init__(parent)
        if value is not None and not isinstance(value, Integer):
            value = Integer(value)

        self._value = None
        self._options = options

        self.setFocusPolicy(Qt.TabFocus)
        for _option in self._options:
            self.addItem(_option)
        
        self.value_changed = Notification()
        self.currentIndexChanged.connect(self._set_value)
        self._set_value((value.get_value() if value is not None
                         else Integer.default().get_value()))
    
    def _set_value(self, value: int):
        """Set the value stored by the input."""
        _value = min(max(value, 0), len(self._options))
        if self.currentIndex() != _value:
            self.setCurrentIndex(_value)
        if(self._value is None or self._value != _value):
            self._value = _value
            self.value_changed.emit(self.get_value())
    
    def get_value(self) -> Integer:
        """Return the value."""
        return Integer(self._value)
    
    def get_int_value(self) -> int:
        """Return the value."""
        return self._value