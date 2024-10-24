"""
Represents a N-dimensional array.

This module defines the NDArray DataType, which represents a matrix
of numbers. It is stored as a numpy array and can be of a defined
numpy dtype and shape.
"""

from datatypes.datatype import DataType
from typing import Union, Tuple, Type, Any, Callable
import numpy as np


class NDArray(DataType):
    """Represents a N-dimensional array."""

    _value: np.ndarray
    _shape: Tuple[int, ...]
    _dtype: Type

    def __init__(self,
                 *values: Tuple[Any, ...],
                 dtype: Type = None,
                 shape: Union[Tuple[int, ...], int] = None):
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
            if (isinstance(shape, np.ndarray)
                or isinstance(shape, list)
                    or isinstance(shape, tuple)):
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
                if (isinstance(values[0], np.ndarray)
                    or isinstance(values[0], list)
                        or isinstance(values[0], tuple)):
                    self._value = np.array(values, dtype=self._dtype)
                else:
                    self._value = np.reshape(
                        values, self._shape).astype(self._dtype)

            if self._value.shape != self._shape:
                raise ValueError(f"Trying to create {type(self).__name__}"
                                 f" with illicit shape {self._value.shape}")

    def _combine(self,
                 other,
                 function: Callable[[Any, Any], Any]
                 ) -> "NDArray":
        """Combine this array with another using a specified function."""
        if isinstance(other, self.__class__):
            return self.__class__(function(self._value, other._value))
        else:
            return self.__class__(function(self._value,
                                           np.array(other, dtype=self._dtype)))
