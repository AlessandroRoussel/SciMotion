"""
Represents an effect that the user can apply to layers.

The Effect class contains a reference to a program that the rendering
pipeline can apply to a layer, and a list of EffectParameter that
lay out a model for which Parameter objects to create when
instanciating the Effect, for the user to adjust.
"""

from enum import Enum
from typing import Set, List

from editing.entities.effect_parameter import EffectParameter


class EffectFlags(Enum):
    """Enumerate all the flags an effect can exhibit."""

    WRITEONLY = 0


class Effect:
    """Represents an effect that the user can apply to layers."""

    _title: str
    _flags: Set[str]
    _parameter_list: List[EffectParameter]

    def __init__(self):
        self._title = ""
        self._flags = set()
        self._parameter_list = []
