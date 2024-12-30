"""A dialog for setting sequence parameters."""

from PySide6.QtCore import Qt, QSize, QLocale
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QWidget,
                               QHBoxLayout, QLabel, QPushButton, QLayout)

from utils.config import Config
from core.entities.sequence import Sequence
from gui.views.inputs.text_input import TextInput
from gui.views.inputs.integer_input import IntegerInput
from gui.views.inputs.type_number_input import TypeNumberInput
from gui.views.inputs.time_input import TimeInput
from gui.services.dialog_service import DialogService


class SequenceDialog(QDialog):
    """A dialog for setting sequence parameters."""

    _title_input: TextInput
    _width_input: IntegerInput
    _height_input: IntegerInput
    _fps_input: TypeNumberInput
    _duration_input: TimeInput
    _ok_button: QPushButton


    def __init__(self, sequence: Sequence = None):
        super().__init__()
        _create = sequence is None

        if _create:
            _title = Config.sequence.default_title
            _width = Config.sequence.default_width
            _height = Config.sequence.default_height
            _frame_rate = Config.sequence.default_frame_rate
            _duration = Config.sequence.default_duration
        else:
            _title = sequence.get_title()
            _width = sequence.get_width()
            _height = sequence.get_height()
            _frame_rate = sequence.get_frame_rate()
            _duration = sequence.get_duration()

        self.setWindowTitle("Create new sequence" if _create
                            else "Sequence parameters")
        self.setWindowIcon(QIcon(Config.app.icon))
        self.setFixedSize(QSize(400, 250))

        _layout = QVBoxLayout()
        _layout.setContentsMargins(40, 20, 40, 20)
        self.setFocusPolicy(Qt.ClickFocus)

        # Line edits:
        self._title_input = TextInput(self, _title, not_empty=True)
        self._width_input = IntegerInput(self, _width, min=1)
        self._height_input = IntegerInput(self, _height, min=1)
        self._fps_input = TypeNumberInput(self, _frame_rate, min=.01, decimals=1)
        self._duration_input = TimeInput(self, _duration, _frame_rate, min=1)

        self._fps_input.value_changed.connect(self.changed_frame_rate)
        self._title_input.selectAll()
        
        # Add line edits to layouts:
        DialogService.add_input(self, _layout, "Title", self._title_input)
        DialogService.add_input(self, _layout, "Width", self._width_input, "px")
        DialogService.add_input(self, _layout, "Height", self._height_input, "px")
        DialogService.add_input(self, _layout, "Frame rate", self._fps_input, "f/s")
        DialogService.add_input(self, _layout, "Duration", self._duration_input)

        DialogService.add_ok_cancel(
            self, _layout, ok_text="Create sequence" if _create else "Apply")
        self.setLayout(_layout)

    def get_values(self) -> tuple[str, int, int, float, int]:
        """Return the user inputs."""
        _title = self._title_input.get_value()
        _width = self._width_input.get_int_value()
        _height = self._height_input.get_int_value()
        _frame_rate = self._fps_input.get_float_value()
        _duration = self._duration_input.get_value()
        return _title, _width, _height, _frame_rate, _duration

    def changed_frame_rate(self):
        """Handle changing the frame rate."""
        _frame_rate = self._fps_input.get_float_value()
        self._duration_input.change_frame_rate(_frame_rate)
