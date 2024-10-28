"""
Represents a generic visual layer with basic geometry.

The abstract class VisualLayer extends the Layer class with
visual and geometric properties, such as position, scale,
rotation, opacity, or blend mode...
"""

from data_types.number import Number
from data_types.vector2 import Vector2
from core.entities.layer import Layer
from core.entities.parameter import Parameter


class VisualLayer(Layer):
    """Represents a generic visual layer with basic geometry."""

    _position: Parameter
    _anchor: Parameter
    _scale: Parameter
    _rotation: Parameter
    _opacity: Parameter

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int):
        super().__init__(title, start_frame, end_frame)
        self._position = Parameter(accepts_keyframes=True,
                                   data_type=Vector2,
                                   default_value=Vector2([.5, .5]))
        self._anchor = Parameter(accepts_keyframes=True,
                                 data_type=Vector2,
                                 default_value=Vector2([.5, .5]))
        self._scale = Parameter(accepts_keyframes=True,
                                data_type=Vector2,
                                default_value=Vector2([1, 1]))
        self._rotation = Parameter(accepts_keyframes=True,
                                   data_type=Number,
                                   default_value=Number(0))
        self._opacity = Parameter(accepts_keyframes=True,
                                  data_type=Number,
                                  default_value=Number(1))

    def get_position(self) -> Parameter:
        """Return the position Parameter."""
        return self._position

    def get_anchor(self) -> Parameter:
        """Return the anchor Parameter."""
        return self._anchor

    def get_scale(self) -> Parameter:
        """Return the scale Parameter."""
        return self._scale

    def get_rotation(self) -> Parameter:
        """Return the rotation Parameter."""
        return self._rotation

    def get_opacity(self) -> Parameter:
        """Return the opacity Parameter."""
        return self._opacity
