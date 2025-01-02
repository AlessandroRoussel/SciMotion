"""
Represents a sRGB color in RGBA floating point format.

This module defines the Color DataType, which represents a sRGB color in
rgba floating point format. It is stored as a numpy float32 4D vector.
"""

from enum import Enum
from typing import Union, Self

import numpy as np

from data_types.ndarray import NDArray
from utils.color_management import ColorSpace, ColorManagement


class Color(NDArray):
    """Represents a sRGB color in RGBA floating point format."""

    _color_space: ColorSpace
    _value: np.ndarray
    _other_spaces_values: dict[ColorSpace, np.ndarray]

    def __init__(self,
                 *values: Union[tuple[float, float, float, float],
                                tuple[float, float, float],
                                list[float],
                                np.ndarray,
                                float],
                 color_space:ColorSpace = ColorSpace.LINEAR):
        self._color_space = color_space
        # Initialize opaque color
        if len(values) == 3:
            super().__init__(*values, 1, dtype=np.float32, shape=4)
        elif len(values) == 1:
            if not NDArray.is_array(values[0]):
                super().__init__(*[values[0] for i in range(3)], 1,
                                 dtype=np.float32, shape=4)
            elif len(values[0]) == 3:
                super().__init__(*[x for x in values[0]], 1,
                                 dtype=np.float32, shape=4)
            elif len(values[0]) == 1:
                super().__init__(*[values[0][0] for i in range(3)], 1,
                                 dtype=np.float32, shape=4)

            # Initialize RGBA color
            else:
                super().__init__(*values, dtype=np.float32, shape=4)
        else:
            super().__init__(*values, dtype=np.float32, shape=4)
        self._other_spaces_values = dict()
    
    def __repr__(self):
        """Return a string representation of the Color."""
        _string = f"{self._value}"[1:-1]
        _color_space_name = f"{self._color_space}".split(".")[-1]
        return f"{type(self).__name__}.{_color_space_name}({_string})"

    def __add__(self, other: Self) -> Self:
        """Add two colors in linear color space."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Impossible to add {self} and {other}.")
        return self.__class__(self.get_value() + other.get_value())

    def __sub__(self, other: Self) -> Self:
        """Subtract two colors in linear color space."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Impossible to subtract {self} and {other}.")
        return self.__add__(other.__mul__(-1))

    def __mul__(self, factor: float) -> Self:
        """Multiply by a float factor in linear color space."""
        return self.__class__(self.get_value() * factor)

    def __truediv__(self, factor: float) -> Self:
        """Divide by a float factor."""
        return self.__mul__(1/factor)

    def clip(self, min_value: Self, max_value: Self) -> Self:
        """Return a color clipped between min and max in linear RGB."""
        value = self.get_value()
        if min_value is not None:
            value = np.maximum(min_value.get_value(), value)
        if max_value is not None:
            value = np.minimum(max_value.get_value(), value)
        return self.__class__(value)

    def get_value(self, color_space=ColorSpace.LINEAR):
        """Return the color as a float array in a given color space."""
        if color_space==self._color_space:
            return self._value
        if color_space not in self._other_spaces_values:
            self._other_spaces_values[color_space] = ColorManagement.convert(
                self._value, self._color_space, color_space)
        return self._other_spaces_values[color_space]

    def get_color_space(self) -> ColorSpace:
        """Return the color space used to define the color."""
        return self._color_space


Color.TRANSPARENT = Color(0, 0, 0, 0, color_space=ColorSpace.SRGB)
Color.BLACK = Color(0, color_space=ColorSpace.SRGB)
Color.GRAY = Color(.5, color_space=ColorSpace.SRGB)
Color.WHITE = Color(1, color_space=ColorSpace.SRGB)
Color.RED = Color(1, 0, 0, color_space=ColorSpace.SRGB)
Color.GREEN = Color(0, 1, 0, color_space=ColorSpace.SRGB)
Color.BLUE = Color(0, 0, 1, color_space=ColorSpace.SRGB)
Color.YELLOW = Color(1, 1, 0, color_space=ColorSpace.SRGB)
Color.MAGENTA = Color(1, 0, 1, color_space=ColorSpace.SRGB)
Color.CYAN = Color(0, 1, 1, color_space=ColorSpace.SRGB)
