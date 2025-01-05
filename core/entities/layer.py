"""
Represents a generic layer within a Sequence.

The abstract class Layer has display properties, such as a title,
as well as sequence related properties, such as a start frame and
an end frame. This abstract class can be implemented to represent
any type of layer such as a video, an image, an audio, a text...
A Layer also holds a list of Modifier that are applied to it.
"""

from data_types.data_type import DataType
from core.entities.modifier import Modifier
from core.entities.parameter import Parameter
from core.entities.parameter_template import ParameterTemplate
from core.services.animation_service import AnimationService


class Layer:
    """Represents a generic Layer within a Sequence."""

    _title: str
    _start_frame: int
    _end_frame: int
    _modifier_list: list[Modifier]
    _properties: dict[str, Parameter]

    _properties_templates: dict[str, ParameterTemplate] = dict()

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int):
        self._title = title
        self.set_start_frame(start_frame)
        self.set_end_frame(end_frame)
        self._modifier_list = []
        self._properties = dict()
        for _name_id, _property_template in self._properties_templates.items():
            _property = AnimationService.parameter_from_template(
                _property_template)
            self._properties[_name_id] = _property

    def get_properties_templates(self) -> dict[str, ParameterTemplate]:
        """Return the properties templates."""
        return self._properties_templates

    def get_modifier_list(self) -> list[Modifier]:
        """Return a reference to the modifier list."""
        return self._modifier_list
    
    def get_property(self, name_id: str) -> DataType:
        """Return a property of the Layer."""
        return self._properties[name_id].get_current_value()

    def get_property_parameter(self, name_id: str) -> Parameter:
        """Return a property Parameter of the Layer."""
        return self._properties[name_id]

    def set_property(self, name_id: str, value: DataType):
        """Set a property of the Layer."""
        return self._properties[name_id].set_current_value(value)

    def get_start_frame(self) -> int:
        """Return the layer start frame."""
        return self._start_frame

    def get_end_frame(self) -> int:
        """Return the layer end frame."""
        return self._end_frame

    def set_start_frame(self, frame: int):
        """Set the layer start frame."""
        self._start_frame = frame

    def set_end_frame(self, frame: int):
        """Set the layer end frame."""
        self._end_frame = frame

    def get_title(self) -> str:
        """Return the layer title."""
        return self._title
