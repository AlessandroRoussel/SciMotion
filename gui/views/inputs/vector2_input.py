"""An input for entering a Vector2."""

from typing import Union

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt

from data_types.number import Number
from data_types.vector2 import Vector2
from gui.views.inputs.number_input import NumberInput
from utils.notification import Notification
from utils.config import Config


class Vector2Input(QWidget):
    """An input for entering a Vector2."""

    _inputs: list[NumberInput]
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Vector2 = None,
                 min: Vector2 = Vector2.negInfinity,
                 max: Vector2 = Vector2.Infinity,
                 decimals: int = 4,
                 step: float = .001):
        super().__init__(parent)
        if value is not None and not isinstance(value, Vector2):
            value = Vector2(value)
        if min is not None and not isinstance(min, Vector2):
            min = Vector2(min)
        if max is not None and not isinstance(max, Vector2):
            max = Vector2(max)

        self._inputs = []
        self.value_changed = Notification()
        for _i in range(2):
            self._inputs.append(
                NumberInput(self, value.get_value()[_i],
                            min.get_value()[_i], max.get_value()[_i],
                            decimals, step))
            self._inputs[_i].value_changed.connect(self._input_changed)

        _layout = QHBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(0)
        self.setLayout(_layout)
        _layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for _i in range(2):
            _layout.addWidget(self._inputs[_i])
        _layout.addStretch()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def _input_changed(self, value: Number):
        """Propagate notification of changing one of the inputs."""
        self.value_changed.emit(self.get_value())

    def get_value(self) -> Vector2:
        """Return the value."""
        _values = [_input.get_float_value() for _input in self._inputs]
        return Vector2(_values)
