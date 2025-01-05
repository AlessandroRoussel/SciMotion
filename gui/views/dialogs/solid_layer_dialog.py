"""A dialog for setting solid layer parameters."""

from PySide6.QtCore import Qt, QSize, QLocale
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QWidget,
                               QHBoxLayout, QLabel, QPushButton, QFrame)

from utils.config import Config
from core.entities.sequence import Sequence
from gui.views.inputs.text_input import TextInput
from gui.views.inputs.integer_input import IntegerInput
from gui.views.inputs.color_input import ColorInput
from gui.services.dialog_gui_service import DialogGUIService
from core.entities.solid_layer import SolidLayer
from data_types.integer import Integer
from data_types.color import Color


class SolidLayerDialog(QDialog):
    """A dialog for setting solid layer parameters."""

    _title_input: TextInput
    _width_input: IntegerInput
    _height_input: IntegerInput
    _color_input: ColorInput


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
            _width = layer.get_property("width")
            _height = layer.get_property("height")
            _color = layer.get_property("color")

        self.setWindowTitle("Create new solid layer" if _create
                            else "Solid layer parameters")
        self.setWindowIcon(QIcon(Config.app.icon))
        self.setFixedSize(QSize(400, 250))

        _layout = QVBoxLayout()
        _layout.setContentsMargins(40, 20, 40, 20)
        self.setFocusPolicy(Qt.ClickFocus)

        # Line edits:
        self._title_input = TextInput(self, _title, not_empty=True)
        self._width_input = IntegerInput(self, _width, min=1)
        self._height_input = IntegerInput(self, _height, min=1)
        self._color_input = ColorInput(self, _color)

        self._title_input.selectAll()
        
        # Add line edits to layouts:
        DialogGUIService.add_input(self, _layout, "Title", self._title_input)
        DialogGUIService.add_input(self, _layout, "Width", self._width_input, "px")
        DialogGUIService.add_input(self, _layout, "Height", self._height_input, "px")
        DialogGUIService.add_input(self, _layout, "Color", self._color_input)
        
        DialogGUIService.add_ok_cancel(
            self, _layout, ok_text="Create layer" if _create else "Apply")
        self.setLayout(_layout)

    def get_values(self) -> tuple[str, Integer, Integer, Color]:
        """Return the user inputs."""
        _title = self._title_input.get_value()
        _width = self._width_input.get_value()
        _height = self._height_input.get_value()
        _color = self._color_input.get_value()
        return _title, _width, _height, _color
