"""
Represents a floating point 2D vector.

This module defines the Vector2 DataType, which represents a floating
point 2D vector. It is stored as a numpy float32 array with 2 entries.
"""

import numpy as np

from datatypes.ndarray import NDArray


class Vector2(NDArray):
    """Represents a floating point 2D vector."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value, dtype=np.float32, shape=2)
