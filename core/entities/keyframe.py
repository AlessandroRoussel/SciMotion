"""
Represents a Keyframe for a Parameter.

A Keyframe marks a point in time within an animation where a
specific value for a Parameter is set. Keyframe objects are
used to create transitions between different values.
"""

from enum import Enum
from typing import Self

from utils.interpolate import Interpolate
from data_types.data_type import DataType


class KeyframeType(Enum):
    """Enumerate all the interpolation types."""

    CONSTANT = 0
    LINEAR = 1
    BEZIER = 2
    BEZIER_LEFT = 3
    BEZIER_RIGHT = 4


class Keyframe:
    """Represents a Keyframe for a Parameter."""

    _frame: int
    _value: DataType
    _keyframe_type: KeyframeType
    _left_handle: tuple[float, DataType]    # tuple[influence, -offset]
    _right_handle: tuple[float, DataType]    # tuple[influence, offset]

    def __init__(self,
                 frame: int,
                 value: DataType,
                 keyframe_type: KeyframeType = KeyframeType.LINEAR,
                 left_handle: tuple[float, DataType] = None,
                 right_handle: tuple[float, DataType] = None):
        self._frame = frame
        self._value = value
        self._keyframe_type = keyframe_type
        if left_handle is None:
            self._left_handle = (1/3, value.default())
        else:
            self._left_handle = left_handle
        if right_handle is None:
            self._right_handle = (1/3, value.default())
        else:
            self._right_handle = right_handle

    def get_frame(self):
        """Return the frame number."""
        return self._frame

    def get_value(self):
        """Return the value."""
        return self._value

    def interpolate_to(self, keyframe_b: Self, t: float) -> DataType:
        """Interpolate from this keyframe to another with factor t."""
        _value_a = self._value
        _type_a = self._keyframe_type
        _value_b = keyframe_b._value
        _type_b = keyframe_b._keyframe_type

        # Constant keyframe.
        if _type_a == KeyframeType.CONSTANT:
            return _value_a

        # Linear interpolation.
        if (_type_a in [KeyframeType.LINEAR,
                        KeyframeType.BEZIER_LEFT]
            and (_type_b in [KeyframeType.CONSTANT,
                             KeyframeType.LINEAR,
                             KeyframeType.BEZIER_RIGHT])):
            return Interpolate.linear(_value_a, _value_b, t)

        # Right bezier interpolation.
        if (_type_a in [KeyframeType.LINEAR,
                        KeyframeType.BEZIER_LEFT]
            and (_type_b in [KeyframeType.BEZIER_RIGHT,
                             KeyframeType.BEZIER])):
            _handle_b = keyframe_b._left_handle
            _value_handle_b = _value_b - _handle_b[1]
            _t2 = 1 - _handle_b[0]
            return Interpolate.cubic_bezier_2d_handles(
                _value_a, _value_a, _value_handle_b, _value_b, 0, _t2, t)

        # Left bezier interpolation.
        if (_type_a in [KeyframeType.BEZIER_RIGHT,
                        KeyframeType.BEZIER]
            and (_type_b in [KeyframeType.CONSTANT,
                             KeyframeType.LINEAR,
                             KeyframeType.BEZIER_RIGHT])):
            _handle_a = self._right_handle
            _value_handle_a = _value_a + _handle_a[1]
            _t1 = _handle_a[0]
            return Interpolate.cubic_bezier_2d_handles(
                _value_a, _value_handle_a, _value_b, _value_b, _t1, 1, t)

        # Left-Right bezier interpolation.
        if (_type_a in [KeyframeType.BEZIER_RIGHT,
                        KeyframeType.BEZIER]
            and (_type_b in [KeyframeType.BEZIER_LEFT,
                             KeyframeType.BEZIER])):
            _handle_a = self._right_handle
            _handle_b = keyframe_b._left_handle
            _value_handle_a = _value_a + _handle_a[1]
            _value_handle_b = _value_b - _handle_b[1]
            _t1 = _handle_a[0]
            _t2 = 1 - _handle_b[0]
            return Interpolate.cubic_bezier_2d_handles(
                _value_a, _value_handle_a, _value_handle_b, _value_b,
                _t1, _t2, t)

        return _value_a
