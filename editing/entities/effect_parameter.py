"""
Represents a parameter of an effect that the user can interact with.

The EffectParameter class describes a model for the Parameter object
that must be created when the user applies an Effect to a layer. It
not only contains information on the type of Parameter (data type,
default, minimum and maximum values...) but also a specific
uniform name used by the rendering pipeline to identify,
the parameter, and information about how the GUI should
display the parameter for the user.
"""

from typing import Type

from datatypes.datatype import DataType


class EffectParameter:
    """Represents an effect that the user can apply to layers."""

    # Unique identifier
    _uniform_name: str

    # Display properties
    _title: str

    # Parameter properties
    _data_type: Type[DataType]
    _default_value: DataType
    _min_value: DataType
    _max_value: DataType

    def __init__(self):
        self._uniform_name = ""
        self._title = ""
        self._data_type = DataType
        self._default_value = DataType.default()
        self._min_value = None
        self._max_value = None
