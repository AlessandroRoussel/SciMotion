"""
Assigns a unique name to each allowed DataType.

This Enum class maps each permissible DataType
class that a Parameter object can use.
"""

from enum import Enum

from data_types.number import Number
from data_types.vector2 import Vector2
from data_types.vector3 import Vector3
from data_types.integer import Integer
from data_types.boolean import Boolean
from data_types.color import Color


class DataTypeName(Enum):
    """Assigns a unique name to each allowed DataType."""

    NUMBER = Number
    VECTOR2 = Vector2
    VECTOR3 = Vector3
    INTEGER = Integer
    BOOLEAN = Boolean
    COLOR = Color
