"""
Represents an instance of the interface for a Modifier.

An ModifierInterface is an object which represents an instance
of a Modifier applied to a Layer. It has Parameter values
depending on the ModifierTemplate it is based on.
"""

from typing import List

from editing.entities.parameter import Parameter


class ModifierInterface:
    """Represents an instance of the interface for a Modifier."""

    _modifier_unique_name: str
    _parameter_list: List[Parameter]

    def __init__(self, modifier_unique_name: str):
        self._modifier_unique_name = modifier_unique_name
        self._parameter_list = []
