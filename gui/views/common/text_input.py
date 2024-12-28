"""A line edit input for entering text."""

from PySide6.QtWidgets import QLineEdit, QWidget


class TextInput(QLineEdit):
    """A line edit input for entering text."""

    _not_empty: bool

    def __init__(self,
                 parent: QWidget = None,
                 text: str = "",
                 not_empty: bool = False):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet("padding: 4px 8px;")
        self._not_empty = not_empty
    
    def is_valid(self) -> bool:
        """Return if the input text is valid."""
        return self.text().strip() != "" if self._not_empty else True
    
    def get_value(self) -> str:
        """Return the value."""
        return self.text().strip()