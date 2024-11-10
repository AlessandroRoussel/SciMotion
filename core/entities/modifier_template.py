"""
Represents a template for instanciating Modifier objects.

The ModifierTemplate class contains a reference to a Modifier that the
rendering pipeline can apply to a layer, and a list of ParameterTemplate
that lay out a model for which Parameter objects to create when
instanciating the interface, for the user to adjust.
"""

from enum import Enum
from typing import Callable

from core.entities.parameter_template import ParameterTemplate


class ModifierFlag(Enum):
    """Enumerate all the flags a Modifier can exhibit."""

    WRITEONLY = 0


class ModifierTemplate:
    """Represents a template for instanciating Modifier objects."""

    _title: str
    _flags: set[ModifierFlag]
    _parameter_template_list: list[ParameterTemplate]
    _apply_function: Callable

    def __init__(self,
                 apply_function: Callable,
                 title: str = "",
                 flags: set[ModifierFlag] = set(),
                 parameter_template_list: list[ParameterTemplate] = []):
        self._title = title
        self._parameter_template_list = parameter_template_list
        self._apply_function = apply_function
        self._flags = flags

    def get_parameter_template_list(self) -> list[ParameterTemplate]:
        """Retrieve the list of parameter templates."""
        return self._parameter_template_list

    def get_title(self) -> str:
        """Retrieve effect title."""
        return self._title

    def get_apply_function(self) -> Callable:
        """Retrieve the modifier apply function."""
        return self._apply_function

    def get_flags(self) -> set[ModifierFlag]:
        """Retrieve effect flags."""
        return self._flags
