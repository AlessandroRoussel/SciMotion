"""
Represents a generic layer within a Sequence.

The abstract class Layer has display properties, such as a title,
as well as sequence related properties, such as a start frame and
an end frame. This abstract class can be implemented to represent
any type of layer such as a video, an image, an audio, a text...
A Layer also holds a list of Modifier that are applied to it.
"""

from core.entities.modifier import Modifier


class Layer:
    """Represents a generic Layer within a Sequence."""

    _title: str
    _start_frame: int
    _end_frame: int
    _modifier_list: list[Modifier]

    def __init__(self,
                 title: str,
                 start_frame: int,
                 end_frame: int):
        self._title = title
        self.set_start_frame(start_frame)
        self.set_end_frame(end_frame)
        self._modifier_list = []

    def get_modifier_list(self) -> list[Modifier]:
        """Return a reference to the modifier list."""
        return self._modifier_list

    def get_start_frame(self) -> int:
        """Return the layer start frame."""
        return self._start_frame

    def get_end_frame(self) -> int:
        """Return the layer end frame."""
        return self._end_frame

    def set_start_frame(self, frame: int):
        """Set the layer start frame."""
        self._start_frame = frame

    def set_end_frame(self, frame: int):
        """Set the layer end frame."""
        self._end_frame = frame

    def get_title(self) -> str:
        """Return the layer title."""
        return self._title
