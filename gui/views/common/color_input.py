"""An input for picking a color."""

from PySide6.QtWidgets import QPushButton, QWidget, QColorDialog
from PySide6.QtGui import QColor

from data_types.color import Color
from utils.notification import Notification


class ColorInput(QPushButton):
    """An input for picking a color."""

    _value: Color
    _red: float
    _green: float
    _blue: float
    _alpha: float
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Color = None):
        super().__init__(parent)
        self.value_changed = Notification()
        self._value = value if value is not None else Color.BLACK

        _color = self._value.get_value()
        self._red = _color[0]
        self._green = _color[1]
        self._blue = _color[2]
        self._alpha = _color[3]

        self.clicked.connect(self.open_dialog)
        self.update_display()
    
    def is_valid(self) -> bool:
        """Return if the input value is valid."""
        return True
    
    def get_value(self) -> Color:
        """Return the value."""
        return self._value
    
    def update_display(self):
        """Update the displayed color of the input."""
        self.setText(f"({round(self._red, 3)}, {round(self._green, 3)}, "
                     f"{round(self._blue, 3)}, {round(self._alpha, 3)})")
        _red = min(255, max(0, int(round(self._red*255))))
        _green = min(255, max(0, int(round(self._green*255))))
        _blue = min(255, max(0, int(round(self._blue*255))))
        _alpha = min(1, max(0, self._alpha))
        self.setStyleSheet(
            "QPushButton, QPushButton:pressed, QPushButton:hover {"
                f"background-color: rgba({_red},{_green},{_blue},{_alpha});"
                "text-align: left; padding: 4px 8px;"
            "}"
            )

    def open_dialog(self):
        """Open the color picker."""
        _dialog = QColorDialog()
        _dialog.setOption(QColorDialog.ShowAlphaChannel, True)

        _red = min(255, max(0, int(round(self._red*255))))
        _green = min(255, max(0, int(round(self._green*255))))
        _blue = min(255, max(0, int(round(self._blue*255))))
        _alpha = min(255, max(0, int(round(self._alpha*255))))
        _dialog.setCurrentColor(QColor(_red, _green, _blue, _alpha))
        if _dialog.exec():
            _color = _dialog.selectedColor()
            if _color.isValid():
                self._red = _color.redF()
                self._green = _color.greenF()
                self._blue = _color.blueF()
                self._alpha = _color.alphaF()
                self._value = Color(self._red, self._green,
                                    self._blue, self._alpha)
                self.value_changed.emit(self._value)
                self.update_display()