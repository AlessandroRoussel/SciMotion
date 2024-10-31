"""A line edit input for entering an integer."""

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QLineEdit, QWidget
from PySide6.QtGui import QIntValidator


class IntInput(QLineEdit):
    """A line edit input for entering an integer."""

    def __init__(self,
                 parent: QWidget = None,
                 value: int = None,
                 min: int = -(2**31-1),
                 max: int = (2**31-1)):
        super().__init__(parent)
        _text = str(value) if value is not None else ""
        self.setText(_text)
        _validator = QIntValidator(min, max, self)
        _locale = QLocale(QLocale.English, QLocale.UnitedStates)
        _validator.setLocale(_locale)
        self.setValidator(_validator)
    
    def is_valid(self) -> bool:
        """Return if the input value is valid."""
        return self.hasAcceptableInput()
    
    def get_value(self) -> int:
        """Return the value."""
        return int(self.text())