"""
Provides useful information about the sequence context.

A SequenceContext is used to provide a ModifierProgram with various
information about the sequence context, such as the current frame number,
the sequence dimensions, and so on...
"""

import moderngl

from core.entities.gl_context import GLContext
from core.entities.sequence import Sequence


class SequenceContext:
    """Provides useful information about the sequence context."""

    _width: int
    _height: int
    _duration: int
    _frame_rate: float
    _current_frame: int

    def __init__(self, sequence: Sequence, current_frame: int):
        self._width = sequence.get_width()
        self._height = sequence.get_height()
        self._duration = sequence.get_duration()
        self._frame_rate = sequence.get_frame_rate()
        self._current_frame = current_frame

    def get_current_frame(self) -> int:
        """Return the current frame number."""
        return self._current_frame
    
    def get_width(self) -> int:
        """Return the sequence width."""
        return self._width

    def get_height(self) -> int:
        """Return the sequence height."""
        return self._height