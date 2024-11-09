"""
Represents a floating point 3D vector.

This module defines the Vector3 DataType, which represents a floating
point 3D vector. It is stored as a numpy float32 array with 3 entries.
"""

import numpy as np

from data_types.ndarray import NDArray


class Vector3(NDArray):
    """Represents a floating point 3D vector."""

    _value: np.ndarray

    def __init__(self, *values):
        super().__init__(*values, dtype=np.float32, shape=3)
