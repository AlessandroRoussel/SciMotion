"""
Represents a floating point number.

This module defines the Number DataType, which represents a floating
point number. It is stored as a numpy float32 array with 1 entry.
"""

import numpy as np

from data_types.ndarray import NDArray


class Number(NDArray):
    """Represents a floating point number."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value, dtype=np.float32, shape=1)


Number.Infinity = Number(float("inf"))
Number.negInfinity = Number(float("-inf"))