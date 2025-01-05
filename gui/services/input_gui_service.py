"""A set of services for inputs."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QDialog)

from core.entities.parameter_template import ParameterTemplate, ParameterFlag
from core.entities.parameter import Parameter
from data_types.color import Color
from data_types.vector2 import Vector2
from data_types.boolean import Boolean
from data_types.number import Number
from data_types.integer import Integer
from data_types.data_type import DataType
from gui.views.inputs.color_input import ColorInput
from gui.views.inputs.vector2_input import Vector2Input
from gui.views.inputs.boolean_input import BooleanInput
from gui.views.inputs.number_input import NumberInput
from gui.views.inputs.integer_input import IntegerInput
from gui.views.inputs.dropdown_input import DropdownInput
from utils.notification import Notification
from gui.services.modifier_gui_service import ModifierGUIService


class InputGUIService:
    """A set of services for inputs."""
    
    @classmethod
    def input_from_parameter(cls,
                             parent: QWidget,
                             template: ParameterTemplate,
                             parameter: Parameter,
                             sequence_id: int,
                             layer_id: int) -> QWidget:
        """Create a GUI input from a Parameter."""
        _type = template.get_data_type()
        _input = None

        if _type is Color:
            # Color inputs :
            _input = ColorInput(parent, parameter.get_current_value())

        elif _type is Vector2:
            # Vector2 inputs :
            _input = Vector2Input(parent,
                                  parameter.get_current_value(),
                                  min=template.get_min_value(),
                                  max=template.get_max_value())
            
        elif _type is Boolean:
            # Boolean inputs :
            _input = BooleanInput(parent, parameter.get_current_value())

        elif _type is Number:
            # Number inputs :
            _input = NumberInput(parent,
                                 parameter.get_current_value(),
                                 min=template.get_min_value(),
                                 max=template.get_max_value())
            
        elif _type is Integer:
            # Number inputs :
            if template.has_flag(ParameterFlag.DROPDOWN):
                _input = DropdownInput(
                    parent, parameter.get_current_value(),
                    template.get_additional_data("options"))
            else:
                _input = IntegerInput(parent,
                                      parameter.get_current_value(),
                                      min=template.get_min_value(),
                                      max=template.get_max_value())
        
        if _input is None:
            return None
        
        _input.value_changed.connect(
            cls._create_update_function(parameter, sequence_id, layer_id))
        return _input
    
    @classmethod
    def _create_update_function(cls,
                                parameter: Parameter,
                                sequence_id: int,
                                layer_id: int):
        """Create the update function for a parameter."""
        return lambda value: cls._update_parameter_value(
            parameter, value, sequence_id, layer_id)
    
    @staticmethod
    def _update_parameter_value(parameter: Parameter,
                                value: DataType,
                                sequence_id: int,
                                layer_id: int):
        """Update a parameter value."""
        parameter.set_current_value(value)
        ModifierGUIService.update_parameter_signal.emit(sequence_id, layer_id)