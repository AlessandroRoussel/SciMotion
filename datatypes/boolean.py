"""
Represents a boolean.

This module defines the Boolean DataType, which represents a
boolean. It is stored as a numpy bool array with 1 entry.
"""

from datatypes.ndarray import NDArray
import numpy as np


class Boolean(NDArray):
    """Represents a boolean."""

    _value: np.ndarray

    def __init__(self, value: bool):
        super().__init__(value, dtype=np.bool_, shape=1)
