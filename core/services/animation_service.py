"""
Service concerning animation in general.

The AnimationService class defines services within the core
package, concerning animation capabilities. This includes
keyframing, interpolating between keyframes...
"""

from typing import Union

from data_types.data_type import DataType
from core.entities.parameter import Parameter
from core.entities.keyframe import Keyframe


class AnimationService:
    """Service concerning animation in general."""

    @classmethod
    def add_keyframe(cls, parameter: Parameter, keyframe: Keyframe):
        """Add a keyframe to a parameter."""
        if parameter.accepts_keyframes():
            _frame = keyframe.get_frame()
            cls.remove_keyframe_at_frame(parameter, _frame)
            _list = parameter.get_keyframe_list()
            _list.append(keyframe)
            _list.sort(key=lambda _keyframe: _keyframe.get_frame())

    @staticmethod
    def remove_keyframe_at_frame(parameter: Parameter, frame: int):
        """Remove a potential keyframe at a given frame."""
        if parameter.accepts_keyframes():
            _list = parameter.get_keyframe_list()
            for _index in range(len(_list)):
                _keyframe = _list[_index]
                _frame = _keyframe.get_frame()
                if _frame == frame:
                    _list.pop(_index)
                if _frame >= frame:
                    break

    @staticmethod
    def get_value_at_frame(parameter: Parameter,
                           frame: Union[int, float]) -> DataType:
        """Retrieve the value of a parameter at a given frame."""
        if not parameter.accepts_keyframes():
            # The parameter doesn't accept keyframes.
            return parameter.get_current_value()

        _list = parameter.get_keyframe_list()
        if len(_list) == 0:
            # There are no keyframes.
            return parameter.get_current_value()

        if len(_list) == 1:
            # There is only one keyframe.
            return _list[0].get_value()

        # There are at least two keyframes.
        for _index in range(len(_list)):
            _keyframe_b = _list[_index]
            _frame_b = _keyframe_b.get_frame()

            if _frame_b == frame:
                # The frame has a keyframe.
                return _keyframe_b.get_value()

            if _frame_b > frame:
                if _index == 0:
                    # The frame is before the first keyframe.
                    return _keyframe_b.get_value()

                # The frame is between two keyframes.
                _keyframe_a = _list[_index-1]
                _frame_a = _keyframe_a.get_frame()
                _t = (frame-_frame_a)/(_frame_b-_frame_a)
                return _keyframe_a.interpolate_to(_keyframe_b, _t)

        # The frame is after the last keyframe.
        return _list[-1].get_value()
