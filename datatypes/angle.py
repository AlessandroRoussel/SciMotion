"""
Represents a floating point angle.

This module defines the Angle DataType, which represents a floating
point angle, expressed between 0 and 2pi. It is stored as a
numpy float32 array with 1 entry.
"""

from datatypes.number import Number
import numpy as np


class Angle(Number):
    """Represents a floating point angle."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value % (2*np.pi))
