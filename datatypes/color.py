"""
Represents a color in RGBA floating point format.

This module defines the Color DataType, which represents a color in rgba
floating point format. It is stored as a numpy float32 4D vector.
"""

from typing import Union

import numpy as np

from datatypes.ndarray import NDArray


class Color(NDArray):
    """Represents a color in RGBA floating point format."""

    _value: np.ndarray

    def __init__(self, *values: Union[tuple[float, float, float, float],
                                      tuple[float, float, float],
                                      list[float],
                                      np.ndarray,
                                      float]):
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


Color.TRANSPARENT = Color(0, 0, 0, 0)
Color.BLACK = Color(0)
Color.GRAY = Color(.5)
Color.WHITE = Color(1)
Color.RED = Color(1, 0, 0)
Color.GREEN = Color(0, 1, 0)
Color.BLUE = Color(0, 0, 1)
Color.YELLOW = Color(1, 1, 0)
Color.MAGENTA = Color(1, 0, 1)
Color.CYAN = Color(0, 1, 1)
