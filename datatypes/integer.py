"""
Represents an integer number.

This module defines the Integer DataType, which represents an
integer number. It is stored as a numpy int32 array with 1 entry.
"""

import numpy as np
from OpenGL import GL

from datatypes.ndarray import NDArray


class Integer(NDArray):
    """Represents an integer number."""

    _value: np.ndarray

    def __init__(self, value: int):
        super().__init__(value, dtype=np.int32, shape=1)

    def send_to_opengl(self, location: GL.GLint):
        """Set an OpenGL uniform with this value."""
        GL.glUniform1i(location, self._value[0])
