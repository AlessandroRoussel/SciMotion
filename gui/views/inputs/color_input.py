"""An input for picking a color."""

from PySide6.QtWidgets import QPushButton, QWidget, QApplication
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from data_types.color import Color
from utils.notification import Notification
from gui.views.dialogs.color_picker import ColorPicker


class ColorInput(QPushButton):
    """An input for picking a color."""

    _value: Color
    _displayed_rgba: str
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Color = None):
        super().__init__(parent)
        self.value_changed = Notification()
        self._set_value(value if value is not None else Color.default())
        self.clicked.connect(self.open_dialog)
        self.setFixedSize(48, 24)
        self.setCursor(Qt.PointingHandCursor)
    
    def _set_value(self, value: Color):
        """Set the value stored by the input."""
        self._value = value
        _rgba = self._value.get_value()
        _red = min(255, max(0, int(round(_rgba[0]*255))))
        _green = min(255, max(0, int(round(_rgba[1]*255))))
        _blue = min(255, max(0, int(round(_rgba[2]*255))))
        _alpha = min(1, max(0, _rgba[3]))
        self._displayed_rgba = f"rgba({_red},{_green},{_blue},{_alpha})"
        self.value_changed.emit(self.get_value())
        self._update_display()
    
    def get_value(self) -> Color:
        """Return the value."""
        return self._value
    
    def _update_display(self):
        """Update the displayed color of the input."""
        # TODO : display a checkerboard for transparent colors
        _color = QApplication.palette().accent().color()
        _border_rgb = (f"rgb({_color.red()}, {_color.green()}, {_color.blue()})")
        self.setStyleSheet(
            f"""QPushButton, QPushButton:pressed, QPushButton:hover {{
                background-color: {self._displayed_rgba};
                border: 1px solid transparent;
                border-radius: 3px;
            }}
            
            QPushButton:pressed, QPushButton:hover {{
                border: 1px solid {_border_rgb};
            }}""")

    def open_dialog(self):
        """Open the color picker."""
        _dialog = ColorPicker(self._value)
        if _dialog.exec():
            _color = _dialog.get_color()
            self._set_value(_color)