"""
Represents a floating point angle in radians.

This module defines the Angle DataType, which represents a floating
point angle, expressed in radians between 0 and 2pi. It is stored
as a numpy float32 array with 1 entry.
"""

import numpy as np

from datatypes.number import Number


class Angle(Number):
    """Represents a floating point angle in radians."""

    _value: np.ndarray

    def __init__(self, value: float):
        super().__init__(value % (2*np.pi))

    def __repr__(self):
        """Return a string representation of the Angle."""
        string = f"{self._value*180/np.pi}"[1:-1]
        return f"{type(self).__name__}({string}°)"
