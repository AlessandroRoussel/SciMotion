"""
Represents a generic visual layer with basic geometry.

The abstract class VisualLayer extends the Layer class with
visual and geometric properties, such as position, scale,
rotation, opacity, or blend mode...
"""

from data_types.number import Number
from data_types.vector2 import Vector2
from core.entities.layer import Layer
from core.entities.parameter_template import ParameterTemplate


class VisualLayer(Layer):
    """Represents a generic visual layer with basic geometry."""

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
            min_value=Number(0), max_value=Number(1))
    }

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int):
        super().__init__(title, start_frame, end_frame)
