"""
Represents an integer number.

This module defines the Integer DataType, which represents an
integer number. It is stored as a numpy int32 array with 1 entry.
"""

from datatypes.ndarray import NDArray
import numpy as np


class Integer(NDArray):
    """Represents an integer number."""

    _value: np.ndarray

    def __init__(self, value: int):
        super().__init__(value, dtype=np.int32, shape=1)
