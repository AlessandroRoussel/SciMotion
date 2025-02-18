"""
Service concerning modifiers in general.

The ModifierService class defines services within the core
package, concerning modifiers that the user can apply. This
includes loading and managing the modifier repository,
adding modifiers to layers...
"""

from typing import Callable
from pathlib import Path
import importlib.util
import inspect

from data_types.data_type_name import DataTypeName
from core.entities.modifier_template import ModifierTemplate, ModifierFlag
from core.entities.modifier_repository import ModifierRepository
from core.entities.parameter_template import ParameterTemplate, ParameterFlag
from core.services.animation_service import AnimationService
from core.entities.modifier import Modifier
from core.entities.layer import Layer

from utils.config import Config


class ModifierService:
    """Service concerning modifiers in general."""

    _loaded: bool = False
    _modifier_count = 0

    @classmethod
    def load_modifiers_from_directory(cls):
        """Load modifiers from the directory into the ModifierRepository."""
        if cls._loaded:
            return
        _directory = Path(Config().app.modifiers_directory)
        if not _directory.is_dir():
            raise ValueError(f"Trying to load modifiers from "
                             f"invalid directory '{_directory}'")
        _repository = ModifierRepository.get_repository()
        _structure = ModifierRepository.get_structure()
        for _py_file in _directory.rglob("*.py"):
            if _py_file.is_file():
                _name_id, _template = cls.load_modifier_from_file(_py_file)
                if _name_id in _repository:
                    print(f"Modifier '{_name_id}' already in repository")
                    continue
                _repository[_name_id] = _template
                # Append to the sub-folders structure.
                _folder_depth = 0
                _sub_structure = _structure
                _relative_path = _py_file.relative_to(_directory)
                _sub_folders = _relative_path.parts
                while _folder_depth + 1 < len(_sub_folders):
                    _sub_folder = _sub_folders[_folder_depth]
                    if _sub_folder not in _sub_structure:
                        _sub_structure[_sub_folder] = dict()
                    _sub_structure = _sub_structure[_sub_folder]
                    _folder_depth += 1
                _sub_structure[_name_id] = _name_id
                print(f"Loaded modifier '{_name_id}' in repository")
        cls._loaded = True

    @classmethod
    def load_modifier_from_file(cls,
                                py_file: Path
                                ) -> tuple[str, ModifierTemplate]:
        """Load a modifier given its python file."""
        if not py_file.is_file():
            raise ValueError(f"{py_file} is not a file")
        if py_file.suffix != ".py":
            raise ValueError(f"{py_file} is not a *.py file")

        # Load the modifier as a python module
        _spec = importlib.util.spec_from_file_location(
            f"modifier_{cls._modifier_count}", py_file)
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        cls._modifier_count += 1

        # Retrieve modifier attributes
        _name_id = getattr(_module, "_name_id", None)
        if _name_id is None:
            raise AttributeError(f"Couldn't find attribute '_name_id' "
                                 f"in '{py_file.name}'")
        if not isinstance(_name_id, str):
            raise TypeError(f"Attribute '_name_id' in '{py_file.name}' "
                            f"should be a str.")

        _title = getattr(_module, "_title", "")
        if not isinstance(_title, str):
            raise TypeError(f"Attribute '_title' in modifier "
                            f"'{_name_id}' should be a str.")

        _flags = set()
        _flags_list = getattr(_module, "_flags", [])
        if not isinstance(_flags_list, list):
            raise TypeError(f"Attribute '_flags' in modifier "
                            f"'{_name_id}' should be a list of str.")
        for _flag_id in range(len(_flags_list)):
            if not isinstance(_flags_list[_flag_id], str):
                raise TypeError(f"Flag {_flag_id} in modifier "
                                f"'{_name_id}' should be a str.")
            _flag_str = str(_flags_list[_flag_id]).strip().upper()
            if not hasattr(ModifierFlag, _flag_str):
                raise ValueError(f"Unkown flag '{_flag_str}' in "
                                 f"modifier '{_name_id}'")
            _flags.add(getattr(ModifierFlag, _flag_str))

        # Retrieve parameters templates
        _parameters_info = getattr(_module, "_parameters", [])
        if not isinstance(_parameters_info, list):
            raise TypeError(f"Attribute '_parameters' in modifier "
                            f"'{_name_id}' should be a list of dict.")
        _parameter_template_list = cls._create_parameter_list(
            _parameters_info, modifier_name_id=_name_id)

        # Retrieve _apply function
        _apply_function = getattr(_module, "_apply", None)
        if _apply_function is None:
            raise AttributeError(f"Couldn't find '_apply' function "
                                 f"in modifier '{_name_id}'")
        if not callable(_apply_function):
            raise TypeError(f"Attribute '_apply' in modifier "
                            f"'{_name_id}' should be a function.")
        cls._inspect_apply_signature(_apply_function,
                                      _parameter_template_list,
                                      modifier_name_id=_name_id)

        # Return name id and modifier template
        _modifier_template = ModifierTemplate(
            _apply_function, title=_title, flags=_flags,
            parameter_template_list=_parameter_template_list)
        return _name_id, _modifier_template

    @staticmethod
    def _create_parameter_list(info_list: list[dict],
                               modifier_name_id: str = ""
                               ) -> list[ParameterTemplate]:
        """Create a list of ParameterTemplate from a list of dict."""
        _parameter_template_list = []
        _param_count = 0
        for _param_info in info_list:

            if "name_id" not in _param_info:
                AttributeError(f"Parameter #{_param_count} from modifier "
                               f"'{modifier_name_id}' is missing 'name_id'")
            _name_id = _param_info["name_id"]
            if not isinstance(_name_id, str):
                raise TypeError(f"Attribute 'name_id' of parameter "
                                f"#{_param_count} from modifier "
                                f"'{modifier_name_id}' should be a str.")

            if "data_type" not in _param_info:
                AttributeError(f"Parameter #{_param_count} from modifier "
                               f"'{modifier_name_id}' is missing 'data_type'")
            if not isinstance(_param_info["data_type"], str):
                raise TypeError(f"Attribute 'data_type' of parameter "
                                f"#{_param_count} from modifier "
                                f"'{modifier_name_id}' should be a str.")
            _data_type_name = _param_info["data_type"].upper()
            if not hasattr(DataTypeName, _data_type_name):
                AttributeError(f"Parameter #{_param_count} from modifier "
                               f"'{modifier_name_id}' has illicit 'data_type'"
                               f": '{_data_type_name}'")
            _data_type = DataTypeName[_data_type_name].value

            _param_title = ""
            _min_value = None
            _max_value = None
            _default_value = None
            _accepts_keyframes = True
            _flags = set()
            _additional_data = dict()

            if "title" in _param_info:
                _param_title = _param_info["title"]
                if not isinstance(_param_title, str):
                    raise TypeError(f"Attribute 'title' of parameter "
                                    f"#{_param_count} from modifier "
                                    f"'{modifier_name_id}' should be a str.")

            if "min_value" in _param_info:
                _min_value = _data_type(_param_info["min_value"])

            if "max_value" in _param_info:
                _max_value = _data_type(_param_info["max_value"])

            if "default_value" in _param_info:
                _default_value = _data_type(_param_info["default_value"])

            if "accepts_keyframes" in _param_info:
                _accepts_keyframes = _param_info["accepts_keyframes"]
                if not isinstance(_accepts_keyframes, bool):
                    raise TypeError(f"Attribute 'accepts_keyframes' of "
                                    f"parameter #{_param_count} from modifier "
                                    f"'{modifier_name_id}' should be a bool.")
            
            if "flags" in _param_info:
                _raw_flags = _param_info["flags"]
                if not isinstance(_raw_flags, list):
                    raise TypeError(f"Attribute 'flags' of parameter "
                                    f"#{_param_count} from modifier "
                                    f"'{modifier_name_id}' should be "
                                    f"a list of str.")
                for _flag in _raw_flags:
                    if not isinstance(_flag, str):
                        raise TypeError(f"Attribute 'flags' of parameter "
                                        f"#{_param_count} from modifier "
                                        f"'{modifier_name_id}' should be "
                                        f"a list of str.")
                    _flag_str = str(_flag).strip().upper()
                    if not hasattr(ParameterFlag, _flag_str):
                        raise ValueError(f"Unkown flag '{_flag_str}' in "
                                        f"parameter #{_param_count} from "
                                        f"modifier '{modifier_name_id}'.")
                    _flags.add(getattr(ParameterFlag, _flag_str))
            
            if "additional_data" in _param_info:
                _data = _param_info["additional_data"]
                if not isinstance(_data, dict):
                    raise TypeError(f"Attribute 'additional_data' of "
                                    f"parameter #{_param_count} from "
                                    f"modifier '{modifier_name_id}' "
                                    f"should be a dict with str keys.")
                for _key, _value in _data.items():
                    if not isinstance(_key, str):
                        raise TypeError(f"Attribute 'additional_data' of "
                                        f"parameter #{_param_count} from "
                                        f"modifier '{modifier_name_id}' "
                                        f"should be a dict with str keys.")
                    _additional_data[str(_key).strip().lower()] = _value

            _parameter_template = ParameterTemplate(
                _name_id,
                _data_type,
                title=_param_title,
                default_value=_default_value,
                min_value=_min_value,
                max_value=_max_value,
                accepts_keyframes=_accepts_keyframes,
                flags=_flags,
                additional_data=_additional_data
            )
            _parameter_template_list.append(_parameter_template)
            _param_count += 1
        return _parameter_template_list

    @staticmethod
    def _inspect_apply_signature(apply_function: Callable,
                                 template_list: list[ParameterTemplate],
                                 modifier_name_id: str = ""):
        """Check whether the signature of an '_apply' function is valid."""
        _signature = inspect.signature(apply_function)
        _signature_parameters = list(_signature.parameters.values())
        if len(_signature_parameters) != 1+len(template_list):
            _correct_signature = [
                _template.get_name_id() for _template in template_list]
            _correct_signature.insert(0, "_render_context")
            raise TypeError(f"Signature mismatch: Arguments of '_apply' "
                            f"function in modifier '{modifier_name_id}' "
                            f" should be {_correct_signature}")
        if _signature_parameters[0].name != "_render_context":
            raise TypeError(f"Signature mismatch: First argument of '_apply' "
                            f"function in modifier '{modifier_name_id}' "
                            f" should be '_render_context'")
        for _i in range(len(template_list)):
            if (_signature_parameters[_i+1].name
                    != template_list[_i].get_name_id()):
                raise TypeError(f"Signature mismatch: Argument #{_i+1} of "
                                f"'_apply' function in modifier "
                                f"'{modifier_name_id}' should be "
                                f"'{template_list[_i].get_name_id()}'")

    @staticmethod
    def modifier_from_template(modifier_name_id: str) -> Modifier:
        """Create a Modifier based on a ModifierTemplate in the repository."""
        _repository = ModifierRepository.get_repository()
        if modifier_name_id not in _repository:
            raise ValueError(f"Couldn't find '{modifier_name_id}'"
                             f"in the modifiers repository.")
        _template = _repository[modifier_name_id]
        _parameter_list = []
        for _parameter_template in _template.get_parameter_template_list():
            _parameter = AnimationService.parameter_from_template(_parameter_template)
            _parameter_list.append(_parameter)
        _modifier = Modifier(modifier_name_id, _parameter_list)
        return _modifier

    @staticmethod
    def add_modifier_to_layer(modifier: Modifier, layer: Layer):
        """Add a Modifier to a Layer."""
        _modifier_list = layer.get_modifier_list()
        _modifier_list.append(modifier)

    @staticmethod
    def modifier_has_flag(modifier: Modifier, flag: ModifierFlag):
        """Checks if a modifier holds a flag."""
        _template_id = modifier.get_template_id()
        _template = ModifierRepository.get_template(_template_id)
        return flag in _template.get_flags()
