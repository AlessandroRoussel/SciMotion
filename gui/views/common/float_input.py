"""A line edit input for entering a float number."""

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QLineEdit, QWidget
from PySide6.QtGui import QDoubleValidator


class FloatInput(QLineEdit):
    """A line edit input for entering a float number."""

    def __init__(self,
                 parent: QWidget = None,
                 value: float = None,
                 min: float = float("-inf"),
                 max: float = float("inf"),
                 decimals: int = 6):
        super().__init__(parent)
        _text = str(value) if value is not None else ""
        self.setText(_text)
        self.setStyleSheet("padding: 4px 8px;")
        _validator = QDoubleValidator(min, max, decimals, self)
        _locale = QLocale(QLocale.English, QLocale.UnitedStates)
        _validator.setLocale(_locale)
        _validator.setNotation(QDoubleValidator.StandardNotation)
        self.setValidator(_validator)
    
    def is_valid(self) -> bool:
        """Return if the input value is valid."""
        return self.hasAcceptableInput()
    
    def get_value(self) -> float:
        """Return the value."""
        return float(self.text())