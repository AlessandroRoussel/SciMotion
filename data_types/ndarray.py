"""
Represents a N-dimensional array.

This module defines the NDArray DataType, which represents a matrix
of numbers. It is stored as a numpy array and can be of a defined
numpy dtype and shape.
"""

from typing import Union, Type, Any, Self

import numpy as np

from data_types.data_type import DataType


class NDArray(DataType):
    """Represents a N-dimensional array."""

    _value: np.ndarray
    _shape: tuple[int, ...]
    _dtype: Type

    def __init__(self,
                 *values: tuple[Any, ...],
                 dtype: Type = None,
                 shape: Union[tuple[int, ...], int] = None):
        if shape is None:   # There is no mandatory shape.
            if dtype is None:   # There is no mandatory dtype.
                self._value = np.array(values)
                self._dtype = self._value.dtype
                if len(self._value) == 1 and len(self._value.shape) > 1:
                    self._value = self._value[0]
            else:
                self._value = np.array(values, dtype=dtype)
                self._dtype = dtype
            self._shape = self._value.shape

        else:   # There is a mandatory shape.
            if dtype is None:   # There is no mandatory dtype.
                self._dtype = np.array([values[0]]).dtype
            else:
                self._dtype = dtype

            # Make shape attribute a tuple.
            if NDArray.is_array(shape):
                self._shape = tuple(shape)
            else:
                self._shape = (shape,)

            if len(self._shape) == 1:   # We store a 1-dimensional vector.
                if len(values) == 1 and isinstance(values[0], np.ndarray):
                    self._value = values[0].astype(self._dtype)
                elif len(values) == 1 and (isinstance(values[0], list)
                                           or isinstance(values[0], tuple)):
                    self._value = np.array(values[0], dtype=self._dtype)
                else:
                    self._value = np.array(values, dtype=self._dtype)
                    if self._shape[0] > 1 and self._value.shape[0] == 1:
                        self._value = self._value.repeat(self._shape[0])

            elif len(self._shape) > 1:  # We store a multi-dimensional matrix.
                if NDArray.is_array(values[0]):
                    self._value = np.array(values, dtype=self._dtype)
                else:
                    self._value = np.reshape(
                        values, self._shape).astype(self._dtype)

            if self._value.shape != self._shape:
                raise ValueError(f"Trying to create {type(self).__name__}"
                                 f" with illicit shape {self._value.shape}")

    def clip(self, min_value: Self, max_value: Self) -> Self:
        """Return a value clipped between min and max."""
        value = self._value
        if min_value is not None:
            value = np.maximum(min_value._value, value)
        if max_value is not None:
            value = np.minimum(max_value._value, value)
        return self.__class__(value)

    def __repr__(self):
        """Return a string representation of the NDArray."""
        _string = f"{self._value}"[1:-1]
        return f"{type(self).__name__}({_string})"

    def get_value(self):
        """Return the value as a list."""
        if self._shape == (1, ):
            return self._value.tolist()[0]
        return self._value.tolist()

    @staticmethod
    def is_array(val: Any) -> bool:
        """Tells if an object is a numpy array, a list or a tuple."""
        return (isinstance(val, np.ndarray)
                or isinstance(val, list)
                or isinstance(val, tuple))
