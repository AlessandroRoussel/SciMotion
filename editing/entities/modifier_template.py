"""
Represents the interface template of a Modifier.

The ModifierTemplate class contains a reference to a Modifier that the
rendering pipeline can apply to a layer, and a list of ParameterTemplate
that lay out a model for which Parameter objects to create when
instanciating the interface, for the user to adjust.
"""

from enum import Enum
from typing import Set, List

from editing.entities.parameter_template import ParameterTemplate
from rendering.entities.compute_shader import ComputeShader


class ModifierFlags(Enum):
    """Enumerate all the flags a Modifier can exhibit."""

    WRITEONLY = 0


class ModifierTemplate:
    """Represents the interface template of a Modifier."""

    _title: str
    _flags: Set[ModifierFlags]
    _parameter_template_list: List[ParameterTemplate]
    _compute_shader: ComputeShader

    def __init__(self,
                 compute_shader: ComputeShader,
                 title: str = "",
                 flags: Set[str] = set(),
                 parameter_template_list: List[ParameterTemplate] = []):
        self._title = title
        self._parameter_template_list = parameter_template_list
        self._compute_shader = compute_shader
        self._flags = set()
        for _flag in flags:
            if hasattr(ModifierFlags, _flag):
                self._flags.add(ModifierFlags[_flag])
            else:
                raise ValueError(f"Unkown effect flag '{_flag}'")

    def get_parameter_template_list(self) -> List[ParameterTemplate]:
        """Retrieve the list of parameter templates."""
        return self._parameter_template_list

    def get_title(self) -> str:
        """Retrieve effect title."""
        return self._title
