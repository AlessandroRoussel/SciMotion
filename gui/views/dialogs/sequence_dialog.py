"""A dialog for setting sequence parameters."""

from PySide6.QtCore import Qt, QSize, QLocale
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QWidget,
                               QHBoxLayout, QLabel, QPushButton, QFrame)

from utils.config import Config
from core.entities.sequence import Sequence
from gui.views.common.text_input import TextInput
from gui.views.common.int_input import IntInput
from gui.views.common.float_input import FloatInput
from gui.views.common.time_input import TimeInput


class SequenceDialog(QDialog):
    """A dialog for setting sequence parameters."""

    _title_input: TextInput
    _width_input: IntInput
    _height_input: IntInput
    _frame_rate_input: FloatInput
    _duration_input: TimeInput
    _ok_button: QPushButton


    def __init__(self, sequence: Sequence = None):
        super().__init__()
        _create = sequence is None

        if _create:
            _title = Config().sequence.default_title
            _width = Config().sequence.default_width
            _height = Config().sequence.default_height
            _frame_rate = Config().sequence.default_frame_rate
            _duration = Config().sequence.default_duration
        else:
            _title = sequence.get_title()
            _width = sequence.get_width()
            _height = sequence.get_height()
            _frame_rate = sequence.get_frame_rate()
            _duration = sequence.get_duration()

        self.setWindowTitle("Create new sequence" if _create
                            else "Sequence parameters")
        self.setWindowIcon(QIcon(Config().app.icon))
        self.setFixedSize(QSize(400, 250))
        _layout = QVBoxLayout()
        _layout.setContentsMargins(40, 20, 40, 20)

        # Line edits:
        self._title_input = TextInput(self, _title, not_empty=True)
        self._title_input.textChanged.connect(self.validate_inputs)
        self._title_input.selectAll()

        self._width_input = IntInput(self, _width, min=1)
        self._width_input.textChanged.connect(self.validate_inputs)

        self._height_input = IntInput(self, _height, min=1)
        self._height_input.textChanged.connect(self.validate_inputs)

        self._frame_rate_input = FloatInput(self, _frame_rate, min=0.01)
        self._frame_rate_input.textChanged.connect(self.validate_inputs)
        
        self._duration_input = TimeInput(self, _duration, _frame_rate, min=1)
        self._duration_input.textChanged.connect(self.validate_inputs)
        self._duration_input.editingFinished.connect(
            self._duration_input.format)
        
        # Add line edits to layouts:
        _layout.addLayout(
            self.create_input_layout("Title", self._title_input))
        _layout.addLayout(
            self.create_input_layout("Width (px)", self._width_input))
        _layout.addLayout(
            self.create_input_layout("Height (px)", self._height_input))
        _layout.addLayout(
            self.create_input_layout("Frame rate (f/s)", self._frame_rate_input))
        _layout.addLayout(
            self.create_input_layout("Duration", self._duration_input))
        
        # Buttons:
        _button_layout = QHBoxLayout()
        _cancel_button = QPushButton("Cancel", self)
        self._ok_button = QPushButton("Create sequence" if _create
                                          else "Apply", self)
        _cancel_button.clicked.connect(self.reject)
        self._ok_button.clicked.connect(self.accept)
        _button_layout.addStretch()
        _button_layout.addWidget(_cancel_button)
        _button_layout.addWidget(self._ok_button)
        _layout.addLayout(_button_layout)
        self._ok_button.setDefault(True)

        self.setLayout(_layout)
        self.validate_inputs()
    
    def create_input_layout(self, label: str, widget: QWidget) -> QHBoxLayout:
        """Create a horizontal layout with a label for an input."""
        _layout = QHBoxLayout()
        _label = QLabel(f"{label}:", self)
        _label.setFixedWidth(100)
        _label.setAlignment(Qt.AlignRight)
        _layout.addWidget(_label)
        _layout.addWidget(widget)
        return _layout

    def get_values(self) -> tuple[str, int, int, float, int]:
        """Return the user inputs."""
        _title = self._title_input.get_value()
        _width = self._width_input.get_value()
        _height = self._height_input.get_value()
        _frame_rate = self._frame_rate_input.get_value()
        _duration = self._duration_input.get_value()
        return _title, _width, _height, _frame_rate, _duration
    
    def validate_inputs(self):
        """Validate inputs and enable/disable the ok button."""
        _valid_title = self._title_input.is_valid()
        _valid_width = self._width_input.is_valid()
        _valid_height = self._height_input.is_valid()
        _valid_frame_rate = self._frame_rate_input.is_valid()
        _valid_duration = self._duration_input.is_valid()
        self._ok_button.setEnabled(_valid_title
                                   and _valid_width
                                   and _valid_height
                                   and _valid_frame_rate
                                   and _valid_duration)