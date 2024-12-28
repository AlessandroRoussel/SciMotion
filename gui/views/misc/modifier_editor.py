"""
A panel for editing the parameters of a modifier

The ModifierEditor panel provides the user with
an editor for all the parameters of a modifier.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel)

from core.entities.modifier import Modifier
from core.entities.modifier_repository import ModifierRepository
from gui.views.common.color_input import ColorInput
from data_types.color import Color


class ModifierEditor(QWidget):
    """A panel for editing the parameters of a modifier."""

    _title: str
    _inputs: dict[str, QWidget] # name_id, input

    def __init__(self, parent: QWidget, modifier: Modifier):
        super().__init__(parent)
        self.build_from_modifier(modifier)
    
    def build_from_modifier(self, modifier: Modifier):
        """Build GUI from modifier template and data."""
        _template_id = modifier.get_template_id()
        _param_list = modifier.get_parameter_list()
        _template = ModifierRepository.get_template(_template_id)
        self._title = _template.get_title()
        self._inputs = dict()

        _layout = QVBoxLayout()
        self.setLayout(_layout)

        _param_template_list = _template.get_parameter_template_list()
        for _param, _param_template in zip(_param_list, _param_template_list):
            _type = _param_template.get_data_type()

            # TODO: change this:
            if _type is Color:
                _input = ColorInput(self, _param.get_current_value())
                _input.value_changed.connect(_param.set_current_value)
            else:
                continue

            _param_title = _param_template.get_title()
            _layout.addLayout(self.create_input_layout(_param_title, _input))
            self._inputs[_param_template.get_name_id()] = _input
        
        _layout.addStretch()
    
    def get_title(self) -> str:
        """Get modifier title."""
        return self._title

    def create_input_layout(self, label: str, widget: QWidget) -> QHBoxLayout:
        """Create a horizontal layout with a label for an input."""
        _layout = QHBoxLayout()
        _label = QLabel(f"{label}:", self)
        _label.setFixedWidth(100)
        _label.setAlignment(Qt.AlignRight)
        _layout.addWidget(_label)
        _layout.addWidget(widget)
        return _layout