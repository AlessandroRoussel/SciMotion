"""
Represents a Modifier applied to a Layer.

A Modifier represents an instance of a ModifierProgram
which the user has applied to a Layer in a Sequence.
It holds a list of Parameter values, which are based
on the ModifierTemplate it inherits from.
"""

from editing.entities.parameter import Parameter


class Modifier:
    """Represents an instance of the interface for a Modifier."""

    _modifier_template_id: str  # template's name id in the repository
    _parameter_list: list[Parameter]

    def __init__(self,
                 modifier_template_id: str,
                 parameter_list: list[Parameter] = []):
        self._modifier_template_id = modifier_template_id
        self._parameter_list = parameter_list
