"""An input for picking a color."""

from PySide6.QtWidgets import QPushButton, QWidget, QColorDialog

from data_types.color import Color
from utils.notification import Notification


class ColorInput(QPushButton):
    """An input for picking a color."""

    _value: Color
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Color = None):
        super().__init__(parent)
        self.value_changed = Notification()
        self.setText("Choose color...")
        self._value = value if value is not None else Color.BLACK
        self.clicked.connect(self.open_dialog)
    
    def is_valid(self) -> bool:
        """Return if the input value is valid."""
        return True
    
    def get_value(self) -> Color:
        """Return the value."""
        return self._value

    def open_dialog(self):
        """Open the color picker."""
        _color = QColorDialog.getColor()
        if _color.isValid():
            _red = _color.redF()
            _green = _color.greenF()
            _blue = _color.blueF()
            _alpha = _color.alphaF()
            self._value = Color(_red, _green, _blue, _alpha)
            self.value_changed.emit()