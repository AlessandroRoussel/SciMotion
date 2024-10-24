"""
Service concerning animation in general.

The AnimationService class defines services within the editing
package, concerning animation capabilities. This includes
keyframing, interpolating between keyframes...
"""

from utils.singleton import Singleton


class AnimationService(metaclass=Singleton):
    """Service concerning animation in general."""

    def __init__(self):
        pass
