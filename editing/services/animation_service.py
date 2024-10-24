"""
Service concerning animation in general.

The AnimationService class defines services within the editing
package, concerning animation capabilities. This includes
keyframing, interpolating between keyframes...
"""


from utils.singleton import Singleton
from datatypes.datatype import DataType
from editing.entities.parameter import Parameter
from editing.entities.keyframe import Keyframe


class AnimationService(metaclass=Singleton):
    """Service concerning animation in general."""

    def __init__(self):
        pass

    def add_keyframe(parameter: Parameter, keyframe: Keyframe):
        """Add a keyframe to a parameter."""
        pass

    def remove_keyframe(parameter: Parameter, keyframe: Keyframe):
        """Remove a keyframe from a parameter."""
        pass

    def get_value_from_frame(parameter: Parameter, frame: int) -> DataType:
        """Interpolate the value of a parameter at a given frame."""
        return None
