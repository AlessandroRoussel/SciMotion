"""A dialog for setting solid layer parameters."""

from PySide6.QtCore import Qt, QSize, QLocale
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QWidget,
                               QHBoxLayout, QLabel, QPushButton, QFrame)

from utils.config import Config
from core.entities.sequence import Sequence
from gui.views.common.text_input import TextInput
from gui.views.common.int_input import IntInput
from gui.views.common.color_input import ColorInput
from core.entities.solid_layer import SolidLayer
from data_types.color import Color


class SolidLayerDialog(QDialog):
    """A dialog for setting solid layer parameters."""

    _title_input: TextInput
    _width_input: IntInput
    _height_input: IntInput
    _color_input: ColorInput
    _ok_button: QPushButton


    def __init__(self, sequence: Sequence, layer: SolidLayer = None):
        super().__init__()
        _create = layer is None

        if _create:
            _title = Config.solid_layer.default_title
            _width = sequence.get_width()
            _height = sequence.get_height()
            _color = Color.BLACK
        else:
            _title = layer.get_title()
            _width = layer.get_width()
            _height = layer.get_height()
            _color = layer.get_color()

        self.setWindowTitle("Create new solid layer" if _create
                            else "Solid layer parameters")
        self.setWindowIcon(QIcon(Config.app.icon))
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

        self._color_input = ColorInput(self, _color)
        self._color_input.value_changed.connect(self.validate_inputs)
        
        # Add line edits to layouts:
        _layout.addLayout(
            self.create_input_layout("Title", self._title_input))
        _layout.addLayout(
            self.create_input_layout("Width (px)", self._width_input))
        _layout.addLayout(
            self.create_input_layout("Height (px)", self._height_input))
        _layout.addLayout(
            self.create_input_layout("Color", self._color_input))
        
        # Buttons:
        _button_layout = QHBoxLayout()
        _cancel_button = QPushButton("Cancel", self)
        self._ok_button = QPushButton("Create layer" if _create
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

    def get_values(self) -> tuple[str, int, int, Color]:
        """Return the user inputs."""
        _title = self._title_input.get_value()
        _width = self._width_input.get_value()
        _height = self._height_input.get_value()
        _color = self._color_input.get_value()
        return _title, _width, _height, _color

    def validate_inputs(self):
        """Validate inputs and enable/disable the ok button."""
        _valid_title = self._title_input.is_valid()
        _valid_width = self._width_input.is_valid()
        _valid_height = self._height_input.is_valid()
        _valid_color = self._color_input.is_valid()
        self._ok_button.setEnabled(_valid_title
                                   and _valid_width
                                   and _valid_height
                                   and _valid_color)