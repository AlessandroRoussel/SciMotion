"""A line edit input for entering a time."""

from PySide6.QtWidgets import QLineEdit, QWidget
from PySide6.QtGui import QRegularExpressionValidator

from utils.time import Time


class TimeInput(QLineEdit):
    """A line edit input for entering a time."""

    _frame_rate: float
    _min: int
    _max: int

    def __init__(self,
                 parent: QWidget = None,
                 value: int = None,
                 frame_rate: float = 60,
                 min: int = -(2**31-1),
                 max: int = (2**31-1)):
        super().__init__(parent)
        self._frame_rate = frame_rate
        self._min = min
        self._max = max
        _text = self._text_from_value(value) if value is not None else ""
        self.setText(_text)
        _regex = r"(-|\+)?(([0-9]+:)?[0-9]+:)?[0-9]+(\.[0-9]+)?"
        self.setValidator(QRegularExpressionValidator(_regex))
    
    def is_valid(self) -> bool:
        """Return if the input value is valid."""
        _value = self.get_value()
        return (self.hasAcceptableInput()
                and _value >= self._min
                and _value <= self._max)

    def format(self):
        """Format the text within the input."""
        self.setText(self._text_from_value(self.get_value()))

    def get_value(self) -> int:
        """Return the value."""
        if not self.hasAcceptableInput():
            return 0
        _hours, _minutes, _seconds, _frames = 0, 0, 0, 0
        _text = self.text().strip()
        _parts = _text.split(":")
        _sub_parts = _parts[-1].split(".")
        if len(_parts) == 1:
            _seconds = int(_sub_parts[0])
            _frames = int(_sub_parts[1]) if len(_sub_parts) > 1 else 0
        elif len(_parts) == 2:
            _minutes = int(_parts[0])
            _seconds = int(_sub_parts[0])
            _frames = int(_sub_parts[1]) if len(_sub_parts) > 1 else 0
        elif len(_parts) == 3:
            _hours = int(_parts[0])
            _minutes = int(_parts[1])
            _seconds = int(_sub_parts[0])
            _frames = int(_sub_parts[1]) if len(_sub_parts) > 1 else 0
        return int(_frames + (_seconds
                              + _minutes*60
                              + _hours*3600) * self._frame_rate)
    
    def _text_from_value(self, frames: int) -> str:
        """Convert a number of frames into a text."""
        return Time.format_time(frames, self._frame_rate)

    def change_frame_rate(self, frame_rate: float):
        """Change the input's local frame rate."""
        self._frame_rate = frame_rate