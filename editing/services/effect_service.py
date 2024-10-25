"""
Service concerning effects in general.

The EffectService class defines services within the editing
package, concerning effects that the user can apply. This
includes loading and managing the effect repository,
adding effects to layers...
"""

import json
from pathlib import Path

from datatypes import DataTypeName
from utils.singleton import Singleton
from editing.entities.effect import Effect
from editing.entities.effect_repository import EffectRepository
from editing.entities.parameter_template import ParameterTemplate
from rendering.entities.shader_program import ShaderProgram


class EffectService(metaclass=Singleton):
    """Service concerning effects in general."""

    def __init__(self):
        # TODO : load configuration if needed
        pass

    def load_effects_from_directory(self, directory: Path):
        """Load all effects from a directory into the EffectRepository."""
        if not directory.is_dir():
            raise ValueError(f"Trying to load effects from "
                             f"invalid directory '{directory}'")
        _repository = EffectRepository().get_repository()
        for _glsl_file in directory.rglob("*.glsl"):
            if _glsl_file.is_file():
                _json_file = _glsl_file.with_suffix(".json")
                if _json_file.is_file():
                    _unique_name = _glsl_file.stem
                    _glsl_code = _glsl_file.read_text()
                    with _json_file.open("r") as _file:
                        _json_data = json.load(_file)
                    _effect = self.create_effect_from_data(_glsl_code,
                                                           _json_data)
                    _repository[_unique_name] = _effect

    def create_effect_from_data(self, glsl_code, json_data):
        """Load an effect given its glsl and json data."""
        _shader_program = ShaderProgram(glsl_code)
        _title = ""
        _flags = set()
        _parameter_template_list = []
        if "title" in json_data:
            _title = json_data["title"]
        if "flags" in json_data:
            _flags = set(json_data["flags"])
        if "parameters" in json_data:
            _param_count = 0
            for _param in json_data["parameters"]:

                if "uniform_name" not in _param:
                    ValueError(f"Parameter #{_param_count} from effect "
                               f"'{_title}' is missing a uniform_name")
                _uniform_name = _param["uniform_name"]

                if "data_type" not in _param:
                    ValueError(f"Parameter #{_param_count} from effect "
                               f"'{_title}' is missing a data_type")
                _data_type_name = _param["data_type"].upper()

                if not hasattr(DataTypeName, _data_type_name):
                    ValueError(f"Trying to create parameter #{_param_count}"
                               f"from effect '{_title}' with illicit data "
                               f"type '{_data_type_name}'")
                _data_type = DataTypeName[_data_type_name]

                _title = ""
                _min_value = None
                _max_value = None
                _default_value = None
                _accepts_keyframes = True

                if "title" in _param:
                    _title = _param["title"]
                if "min_value" in _param:
                    _min_value = _data_type(_param["min_value"])
                if "max_value" in _param:
                    _max_value = _data_type(_param["max_value"])
                if "default_value" in _param:
                    _default_value = _data_type(_param["default_value"])
                if "accepts_keyframes" in _param:
                    _accepts_keyframes = _param["accepts_keyframes"]

                _parameter_template = ParameterTemplate(
                    _uniform_name,
                    _data_type,
                    title=_title,
                    default_value=_default_value,
                    min_value=_min_value,
                    max_value=_max_value,
                    accepts_keyframes=_accepts_keyframes
                )
                _parameter_template_list.append(_parameter_template)
                _param_count += 1
        return Effect(_shader_program,
                      _title,
                      _flags,
                      _parameter_template_list)
