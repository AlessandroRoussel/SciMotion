"""
Assigns a unique name to each allowed DataType.

This Enum class maps each permissible DataType class that an effect
can use within its JSON parameters to a distinct, descriptive name.
"""

from enum import Enum

from datatypes.number import Number
from datatypes.vector2 import Vector2
from datatypes.vector3 import Vector3
from datatypes.integer import Integer
from datatypes.boolean import Boolean
from datatypes.color import Color
from datatypes.angle import Angle


class DataTypeName(Enum):
    """Assigns a unique name to each allowed DataType."""

    NUMBER = Number
    VECTOR2 = Vector2
    VECTOR3 = Vector3
    INTEGER = Integer
    BOOLEAN = Boolean
    COLOR = Color
    ANGLE = Angle