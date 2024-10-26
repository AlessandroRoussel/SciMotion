"""
Represents an abstract DataType.

This module defines the DataType abstract class, which provides
basic arithmetic operations for data of a specific type. The class
supports addition, subtraction, multiplication, and division,
and can be combined with both instances and numeric values.
"""

from typing import Any, Callable, Self


class DataType:
    """Represents abstract data."""

    _value: Any

    def __init__(self, value):
        self._value = value

    def __add__(self, other) -> Self:
        """Define the + operator."""
        return self._combine(other, self.__class__._add)

    def __sub__(self, other) -> Self:
        """Define the - operator."""
        return self._combine(other, self.__class__._sub)

    def __mul__(self, other) -> Self:
        """Define the * operator."""
        return self._combine(other, self.__class__._mul)

    def __truediv__(self, other) -> Self:
        """Define the / operator."""
        return self._combine(other, self.__class__._div)

    def _combine(self,
                 other,
                 function: Callable[[Any, Any], Any]
                 ) -> Self:
        """Combine this object with another using a specified function."""
        if isinstance(other, self.__class__):
            return self.__class__(function(self._value, other._value))
        else:
            return self.__class__(function(self._value, other))

    def __repr__(self):
        """Return a string representation of the DataType."""
        return f"{type(self).__name__}({self._value})"

    def clip(self, min_value: Self, max_value: Self) -> Self:
        """Return a value clipped between min and max."""
        value = self._value
        if min_value is not None:
            value = max(min_value._value, value)
        if max_value is not None:
            value = min(max_value._value, value)
        return self.__class__(value)

    @classmethod
    def default(cls):
        """Return an instance with default value."""
        return cls(0)

    @staticmethod
    def _add(a, b):
        return a + b

    @staticmethod
    def _sub(a, b):
        return a - b

    @staticmethod
    def _mul(a, b):
        return a * b

    @staticmethod
    def _div(a, b):
        return a / b
