"""
Represents a solid color layer.

The class SolidLayer extends the VisualLayer class
with pixel dimensions and a color. It represents a
solid layer with uniform color.
"""

from data_types.color import Color
from core.entities.visual_layer import VisualLayer
from core.entities.parameter import Parameter


class SolidLayer(VisualLayer):
    """Represents a solid color layer."""

    _width: int
    _height: int
    _color: Parameter

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int,
                 width: int,
                 height: int,
                 color: Color):
        super().__init__(title, start_frame, end_frame)
        self._width = width
        self._height = height
        self._color = Parameter(accepts_keyframes=True,
                                data_type=Color,
                                default_value=color)

    def get_width(self) -> int:
        """Return the layer width."""
        return self._width

    def get_height(self) -> int:
        """Return the layer height."""
        return self._height

    def get_color(self) -> Color:
        """Return the layer color."""
        return self._color
