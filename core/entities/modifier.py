"""
Represents a Modifier applied to a Layer.

A Modifier represents an instance of a ModifierTemplate
which the user has applied to a Layer in a Sequence.
It holds a list of Parameter values, which are based
on the template it inherits from.
"""

from core.entities.parameter import Parameter


class Modifier:
    """Represents a Modifier applied to a Layer."""

    _template_id: str  # template's name id in the repository
    _parameter_list: list[Parameter]

    def __init__(self,
                 template_id: str,
                 parameter_list: list[Parameter] = []):
        self._template_id = template_id
        self._parameter_list = parameter_list

    def get_template_id(self) -> str:
        """Return the parent ModifierTemplate name id."""
        return self._template_id

    def get_parameter_list(self) -> list[Parameter]:
        """Return the list of parameters."""
        return self._parameter_list
