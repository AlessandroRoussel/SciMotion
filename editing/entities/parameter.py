"""
Represents a property that can vary over time.

A Parameter is an object used within an Effect or a Layer which
stores a value of a certain DataType, has default, minimum, and
maximum values and can be keyframed for animations.
"""

from typing import List, Type

from datatypes.entities.datatype import DataType
from editing.entities.keyframe import Keyframe


class Parameter:
    """Represents a property that can vary over time."""

    title: str
    _constant: bool
    _datatype: Type[DataType]
    _current_value: DataType
    _default_value: DataType
    _min_value: DataType
    _max_value: DataType
    _keyframe_list: List[Keyframe]

    def __init__(self,
                 title: str = "",
                 constant: bool = False,
                 datatype: Type[DataType] = DataType,
                 default_value: DataType = None,
                 min_value: DataType = None,
                 max_value: DataType = None):
        self.title = title
        self._datatype = datatype
        self._constant = constant
        if default_value is None:
            self._default_value = datatype.default()
        else:
            self._default_value = default_value
        self._min_value = min_value
        self._max_value = max_value
        self._current_value = self._default_value

        self._keyframe_list = []

    def get_current_value(self) -> DataType:
        """Return the current value stored in the Parameter."""
        return self._current_value

    def set_current_value(self, value: DataType):
        """Change the current value stored in the Parameter."""
        self._current_value = value.clip(self._min_value, self._max_value)
