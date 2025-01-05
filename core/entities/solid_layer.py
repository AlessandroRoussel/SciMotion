"""
Represents a solid color layer.

The class SolidLayer extends the VisualLayer class
with pixel dimensions and a color. It represents a
solid layer with uniform color.
"""

from data_types.number import Number
from data_types.vector2 import Vector2
from data_types.integer import Integer
from data_types.color import Color
from core.entities.visual_layer import VisualLayer
from core.entities.parameter_template import ParameterTemplate


class SolidLayer(VisualLayer):
    """Represents a solid color layer."""

    _properties_templates: dict[str, ParameterTemplate] = {
        "position": ParameterTemplate(
            "position", Vector2, "Position", Vector2([.5, .5])),
        "anchor": ParameterTemplate(
            "anchor", Vector2, "Anchor", Vector2([.5, .5])),
        "scale": ParameterTemplate(
            "scale", Vector2, "Scale", Vector2([1, 1])),
        "rotation": ParameterTemplate(
            "rotation", Number, "Rotation", Number(0)),
        "opacity": ParameterTemplate(
            "opacity", Number, "Opacity", Number(1),
            min_value=Number(0), max_value=Number(1)),

        "width": ParameterTemplate(
            "width", Integer, "Width",
            min_value=Integer(1),
            accepts_keyframes=False),
        "height": ParameterTemplate(
            "height", Integer, "Height",
            min_value=Integer(1),
            accepts_keyframes=False),
        "color": ParameterTemplate(
            "color", Color, "Color")
    }

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int,
                 width: Integer,
                 height: Integer,
                 color: Color):
        super().__init__(title, start_frame, end_frame)
        self.set_property("width", width)
        self.set_property("height", height)
        self.set_property("color", color)
