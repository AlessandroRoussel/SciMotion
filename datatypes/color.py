"""
Represents a color in RGBA floating point format.

This module defines the Color DataType, which represents a color in rgba
floating point format. It is stored as a numpy float32 4D vector.
"""

from datatypes.ndarray import NDArray
from typing import Union, Tuple, List
import numpy as np


class Color(NDArray):
    """Represents a color in RGBA floating point format."""

    _value: np.ndarray

    def __init__(self, *values: Union[Tuple[float, float, float, float],
                                      List[float],
                                      np.ndarray]):
        super().__init__(*values, dtype=np.float32, shape=4)

    BLACK = None


Color.BLACK = Color(0)
