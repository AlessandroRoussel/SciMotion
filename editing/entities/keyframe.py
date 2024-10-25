"""
Represents a Keyframe for a Parameter.

A Keyframe marks a point in time within an animation where a
specific value for a Parameter is set. Keyframe objects are
used to create transitions between different values.
"""

from enum import Enum

from datatypes.datatype import DataType


class KeyframeType(Enum):
    """Enumerate all the interpolation types."""

    LINEAR = 0
    BEZIER = 1
    AUTO = 2
    CUSTOM = 3


class Keyframe:
    """Represents a Keyframe for a Parameter."""

    _frame: int
    _value: DataType
    _interpolation: KeyframeType

    def __init__(self,
                 frame: int,
                 value: DataType,
                 interpolation: KeyframeType = KeyframeType.LINEAR):
        self._frame = frame
        self._value = value
        self._interpolation = interpolation

    def get_frame(self):
        """Return the frame number."""
        return self._frame

    def get_value(self):
        """Return the value."""
        return self._value
