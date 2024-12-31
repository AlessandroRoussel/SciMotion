"""
A panel for editing the parameters of a modifier

The ModifierEditor panel provides the user with
an editor for all the parameters of a modifier.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGridLayout, QLabel,
                               QSizePolicy, QFrame)

from core.entities.modifier import Modifier
from core.entities.parameter import Parameter
from core.entities.modifier_repository import ModifierRepository
from gui.services.modifier_gui_service import ModifierGUIService
from gui.views.inputs.color_input import ColorInput
from gui.views.inputs.vector2_input import Vector2Input
from data_types.data_type import DataType
from data_types.color import Color
from data_types.vector2 import Vector2
from utils.notification import Notification


class ModifierEditor(QFrame):
    """A panel for editing the parameters of a modifier."""

    _title: str
    _inputs: dict[str, QWidget] # name_id, input

    update_parameter_signal: Notification

    def __init__(self, parent: QWidget, modifier: Modifier):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.build_from_modifier(modifier)
        self.update_parameter_signal = Notification()
    
    def build_from_modifier(self, modifier: Modifier):
        """Build GUI from modifier template and data."""
        _template_id = modifier.get_template_id()
        _param_list = modifier.get_parameter_list()
        _template = ModifierRepository.get_template(_template_id)
        self._title = _template.get_title()
        self._inputs = dict()

        _layout = QGridLayout(self)
        _layout.setAlignment(Qt.AlignLeft)
        self.setLayout(_layout)

        _title_widget = QLabel(self._title, self)
        _layout.addWidget(_title_widget, 0, 0, 1, 2)

        _param_template_list = _template.get_parameter_template_list()
        for _i in range(len(_param_template_list)):
            _param = _param_list[_i]
            _param_template = _param_template_list[_i]
            _type = _param_template.get_data_type()

            # TODO: change this:
            if _type is Color:
                _input = ColorInput(self, _param.get_current_value())
            elif _type is Vector2:
                _input = Vector2Input(self, _param.get_current_value())
            else:
                continue

            _input.value_changed.connect(self._create_update_function(_param))
            _param_title = _param_template.get_title()
            _layout.addWidget(QLabel(f"{_param_title}:", self), _i+1, 0)
            _layout.addWidget(_input, _i+1, 1)
            self._inputs[_param_template.get_name_id()] = _input
    
    def get_title(self) -> str:
        """Get modifier title."""
        return self._title
    
    def _create_update_function(self, param: Parameter):
        """Create the update function for a parameter."""
        return lambda value: self._update_parameter_value(param, value)

    def _update_parameter_value(self, param: Parameter, value: DataType):
        """Update a parameter value."""
        param.set_current_value(value)
        self.update_parameter_signal.emit()