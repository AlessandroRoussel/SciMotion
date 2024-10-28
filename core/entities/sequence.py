"""
Represents a video Sequence within a Project.

The class Sequence represents a sequence within a Project, which
holds properties, such as pixel dimensions, duration, or frame rate,
and a pile of Layer of various types. When rendered, a Sequence
combines all its visual layers using blend modes.
"""

from core.entities.layer import Layer


class Sequence:
    """Represents a video Sequence within a Project."""

    _title: str
    _width: int
    _height: int
    _duration: int
    _frame_rate: float
    _layer_list: list[Layer]

    def __init__(self,
                 title: str,
                 width: int,
                 height: int,
                 duration: int,
                 frame_rate: float):
        self._title = title
        self._width = width
        self._height = height
        self._duration = duration
        self._frame_rate = frame_rate
        self._layer_list = []

    def get_width(self) -> int:
        """Return the sequence width."""
        return self._width

    def get_height(self) -> int:
        """Return the sequence height."""
        return self._height

    def get_layer_list(self) -> list[Layer]:
        """Return a reference to the layer list."""
        return self._layer_list
