"""
Represents a floating point number.

This module defines the Number DataType, which represents a floating
point number. It is stored as a numpy float32 array with 1 entry.
"""

import numpy as np
from OpenGL import GL

from datatypes.ndarray import NDArray


class Number(NDArray):
    """Represents a floating point number."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value, dtype=np.float32, shape=1)

    def send_to_opengl(self, location: GL.GLint):
        """Set an OpenGL uniform with this value."""
        GL.glUniform1f(location, self._value[0])
