"""
Represents a template for a parameter in a Modifier.

The ParameterTemplate class describes a template for the Parameter
that must be created when the user applies a Modifier to a layer.
It contains information on the type of Parameter (DataType,
default value, minimum and maximum values...) but also a
unique name_id used to pass values to the rendering pipeline,
as well as information about the parameter for the user.
"""

from enum import Enum
from typing import Type, Union, Any

from data_types.data_type import DataType


class ParameterFlag(Enum):
    """Enumerate all the flags a ParameterTemplate can exhibit."""

    DROPDOWN = 0


class ParameterTemplate:
    """Represents a template for a parameter in a Modifier."""

    # Unique identifier
    _name_id: str

    # Display properties
    _title: str

    # Parameter properties
    _accepts_keyframes: bool
    _data_type: Type[DataType]
    _default_value: DataType
    _min_value: DataType
    _max_value: DataType
    _flags: set[ParameterFlag]
    _additional_data: dict

    def __init__(self,
                 name_id: str,
                 data_type: Type[DataType],
                 title: str = "",
                 default_value: DataType = None,
                 min_value: DataType = None,
                 max_value: DataType = None,
                 accepts_keyframes: bool = True,
                 flags: set[ParameterFlag] = set(),
                 additional_data: dict = dict()):
        self._name_id = name_id
        self._title = title
        self._data_type = data_type
        self._default_value = default_value
        self._min_value = min_value
        self._max_value = max_value
        self._accepts_keyframes = accepts_keyframes
        self._flags = flags
        self._additional_data = additional_data

    def get_name_id(self) -> str:
        """Retrieve the name id."""
        return self._name_id

    def get_title(self) -> str:
        """Retrieve the title."""
        return self._title

    def get_accepts_keyframes(self) -> bool:
        """Retrieve the keyframability."""
        return self._accepts_keyframes

    def get_data_type(self) -> Type[DataType]:
        """Retrieve the data type."""
        return self._data_type

    def get_default_value(self) -> DataType:
        """Retrieve the default value."""
        return self._default_value

    def get_min_value(self) -> DataType:
        """Retrieve the minimum value."""
        return self._min_value

    def get_max_value(self) -> DataType:
        """Retrieve the maximum value."""
        return self._max_value

    def get_flags(self) -> set[ParameterFlag]:
        """Retrieve parameter flags."""
        return self._flags
    
    def has_flag(self, flag: ParameterFlag) -> bool:
        """Return if the ParameterTemplate holds a specific flag."""
        return flag in self._flags
    
    def get_additional_data(self, key: str = None) -> Union[dict, Any]:
        """Retrieve additional data."""
        if key is None:
            return self._additional_data
        else:
            return self._additional_data[key.strip().lower()]
