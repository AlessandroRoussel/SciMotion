"""
Represents an instance of an Effect applied to a Layer.

An EffectInstance is an object which represents an instance
of an Effect applied to this Layer. It has Parameter values
depending on the Effect it is an instance of.
"""

from typing import Dict

from editing.entities.parameter import Parameter


class EffectInstance:
    """Represents an instance of an Effect applied to a Layer."""

    _effect_unique_name: str
    _parameter_dict: Dict[str, Parameter]   # Dict[uniform name: parameter]

    def __init__(self, effect_unique_name: str):
        self._effect_unique_name = effect_unique_name
        self._parameter_dict = dict()
