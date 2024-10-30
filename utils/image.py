"""
Represents an RGBA float32 image.

The Image class represents an RGBA float32 image, and stores
its pixel data along with information such as dimensions.
"""

import numpy as np


class Image:
    """Represents an RGBA float32 image."""

    _width: int
    _height: int
    _data_bytes: bytes
    _data_array: np.ndarray

    def __init__(self,
                 width: int,
                 height: int,
                 data_bytes: bytes = None,
                 data_array: np.ndarray = None):
        self._width = width
        self._height = height
        self._data_bytes = data_bytes
        self._data_array = data_array
        if data_array is None and data_bytes is None:
            data_array = np.zeros((height, width, 4), dtype=np.float32)

    def get_width(self) -> int:
        """Return the image width."""
        return self._width

    def get_height(self) -> int:
        """Return the image height."""
        return self._height

    def get_data_bytes(self) -> bytes:
        """Return the image data in bytes."""
        if self._data_bytes is None:
            self._data_bytes = self._data_array.tobytes()
        return self._data_bytes

    def get_data_array(self) -> np.ndarray:
        """Return the image data as a numpy array."""
        if self._data_array is None:
            self._data_array = np.frombuffer(
                self._data_bytes, dtype=np.float32).reshape(
                    (self._height, self._width, 4))
        return self._data_array
