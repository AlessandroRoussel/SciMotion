"""
Represents a floating point 2D vector.

This module defines the Vector2 DataType, which represents a floating
point 2D vector. It is stored as a numpy float32 array with 2 entries.
"""

import numpy as np
from OpenGL import GL

from datatypes.ndarray import NDArray


class Vector2(NDArray):
    """Represents a floating point 2D vector."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value, dtype=np.float32, shape=2)

    def send_to_opengl(self, location: GL.GLint):
        """Set an OpenGL uniform with this value."""
        GL.glUniform2f(location, self._value[0], self._value[1])
