"""
Represents a template for a parameter in an effect.

The ParameterTemplate class describes a template for the Parameter
that must be created when the user applies an Effect to a layer. It
not only contains information on the type of Parameter (data type,
default, minimum and maximum values...) but also a specific
uniform name used by the rendering pipeline to identify,
the parameter, and information about how the GUI should
display the parameter for the user.
"""

from typing import Type

from datatypes.datatype import DataType


class ParameterTemplate:
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
    _accepts_keyframes: bool

    def __init__(self,
                 uniform_name: str,
                 data_type: Type[DataType],
                 title: str = "",
                 default_value: DataType = None,
                 min_value: DataType = None,
                 max_value: DataType = None,
                 accepts_keyframes: bool = True):
        self._uniform_name = uniform_name
        self._title = title
        self._data_type = data_type
        self._default_value = default_value
        self._min_value = min_value
        self._max_value = max_value
        self._accepts_keyframes = accepts_keyframes

    def get_title(self) -> str:
        """Return title."""
        return self._title

    def get_accepts_keyframes(self) -> bool:
        """Return title."""
        return self._accepts_keyframes

    def get_data_type(self) -> Type[DataType]:
        """Return title."""
        return self._data_type

    def get_default_value(self) -> DataType:
        """Return title."""
        return self._default_value

    def get_min_value(self) -> DataType:
        """Return title."""
        return self._min_value

    def get_max_value(self) -> DataType:
        """Return title."""
        return self._max_value