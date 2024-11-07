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
        self.set_title(title)
        self.set_width(width)
        self.set_height(height)
        self.set_duration(duration)
        self.set_frame_rate(frame_rate)
        self._layer_list = []

    def get_width(self) -> int:
        """Return the sequence width."""
        return self._width

    def get_height(self) -> int:
        """Return the sequence height."""
        return self._height
    
    def get_title(self) -> str:
        """Return the sequence title."""
        return self._title
    
    def get_frame_rate(self) -> float:
        """Return the sequence frame rate."""
        return self._frame_rate
    
    def get_duration(self) -> int:
        """Return the sequence duration."""
        return self._duration

    def set_width(self, width: int):
        """Set the sequence width."""
        self._width = width

    def set_height(self, height: int):
        """Set the sequence height."""
        self._height = height
    
    def set_title(self, title: str):
        """Set the sequence title."""
        self._title = title
    
    def set_frame_rate(self, frame_rate: float):
        """Set the sequence frame rate."""
        self._frame_rate = frame_rate
    
    def set_duration(self, frames: int):
        """Set the sequence duration."""
        self._duration = frames

    def get_layer_list(self) -> list[Layer]:
        """Return a reference to the layer list."""
        return self._layer_list
