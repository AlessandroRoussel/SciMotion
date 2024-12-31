"""An input for entering a Boolean."""

from typing import Union

from PySide6.QtWidgets import QSizePolicy, QCheckBox, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

from data_types.boolean import Boolean
from utils.notification import Notification
from utils.config import Config


class BooleanInput(QWidget):
    """An input for entering a Boolean."""

    _checkbox: QCheckBox
    _value: bool
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Union[Boolean, bool] = None):
        super().__init__(parent)
        if value is not None and not isinstance(value, Boolean):
            value = Boolean(value)
        self._value = None

        _layout = QHBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        self._checkbox = QCheckBox("", self)
        self._checkbox.setCursor(Qt.PointingHandCursor)
        _layout.addWidget(self._checkbox)
        _layout.addStretch()

        self._checkbox.setFocusPolicy(Qt.TabFocus)
        self.value_changed = Notification()
        self._checkbox.checkStateChanged.connect(self._handle_change)
        self._set_value((value.get_value() if value is not None
                         else Boolean.default().get_value()))
    
    def _set_value(self, value: bool):
        """Set the value stored by the input."""
        _prev_value = self._value
        self._value = value
        if(_prev_value is None or _prev_value != self._value):
            self.value_changed.emit(self.get_value())
            self._checkbox.setCheckState(Qt.CheckState.Checked if self._value
                                         else Qt.CheckState.Unchecked)
    
    def _handle_change(self, check_state: Qt.CheckState):
        """Handle changing the check state."""
        self._set_value(check_state == Qt.CheckState.Checked)
    
    def get_value(self) -> Boolean:
        """Return the value."""
        return Boolean(self._value)
    
    def get_bool_value(self) -> bool:
        """Return the value."""
        return self._value