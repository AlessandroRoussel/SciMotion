"""
Represents an abstract DataType.

This module defines the DataType abstract class, which provides
basic arithmetic operations for data of a specific type. The class
supports addition, subtraction, multiplication, and division,
and can be combined with both instances and numeric values.
"""

from typing import Any, Self


class DataType:
    """Represents abstract data."""

    _value: Any

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        """Return a string representation of the DataType."""
        return f"{type(self).__name__}({self._value})"

    def __add__(self, other: Self) -> Self:
        """Add two objects of this data type."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Impossible to add {self} and {other}.")
        return self.__class__(self._value + other._value)

    def __sub__(self, other: Self) -> Self:
        """Subtract two objects of this data type."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Impossible to subtract {self} and {other}.")
        return self.__add__(other.__mul__(-1))

    def __mul__(self, factor: float) -> Self:
        """Multiply by a float factor."""
        return self.__class__(self._value * factor)

    def __truediv__(self, factor: float) -> Self:
        """Divide by a float factor."""
        return self.__mul__(1/factor)

    def clip(self, min_value: Self, max_value: Self) -> Self:
        """Return a value clipped between min and max."""
        value = self._value
        if min_value is not None:
            value = max(min_value._value, value)
        if max_value is not None:
            value = min(max_value._value, value)
        return self.__class__(value)

    def get_value(self):
        """Return the value as a common type."""
        return self._value

    @classmethod
    def default(cls):
        """Return an instance with default value."""
        return cls(0)
