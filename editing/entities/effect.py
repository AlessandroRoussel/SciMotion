"""
Represents an effect that the user can apply to layers.

The Effect class contains a reference to a program that the rendering
pipeline can apply to a layer, and a list of ParameterTemplate that
lay out a model for which Parameter objects to create when
instanciating the Effect, for the user to adjust.
"""

from enum import Enum
from typing import Set, List

from editing.entities.parameter_template import ParameterTemplate
from rendering.entities.shader_program import ShaderProgram


class EffectFlags(Enum):
    """Enumerate all the flags an effect can exhibit."""

    WRITEONLY = 0


class Effect:
    """Represents an effect that the user can apply to layers."""

    _title: str
    _flags: Set[EffectFlags]
    _parameter_template_list: List[ParameterTemplate]
    _shader_program: ShaderProgram

    def __init__(self,
                 shader_program: ShaderProgram,
                 title: str = "",
                 flags: Set[str] = set(),
                 parameter_template_list: List[ParameterTemplate] = []):
        self._title = title
        self._parameter_template_list = parameter_template_list
        self._shader_program = shader_program
        self._flags = set()
        for _flag in flags:
            if hasattr(EffectFlags, _flag):
                self._flags.add(EffectFlags[_flag])
            else:
                raise ValueError(f"Unkown effect flag '{_flag}'")

    def get_parameter_template_list(self) -> List[ParameterTemplate]:
        """Retrieve the list of parameter templates."""
        return self._parameter_template_list

    def get_title(self) -> str:
        """Retrieve effect title."""
        return self._title
