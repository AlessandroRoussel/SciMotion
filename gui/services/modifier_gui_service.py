"""A set of services for modifier related GUI elements."""

from PySide6.QtGui import QStandardItem, QStandardItemModel

from core.entities.modifier_repository import ModifierRepository
from core.services.modifier_service import ModifierService


class ModifierGUIService():
    """A set of services for modifier related GUI elements."""

    @classmethod
    def create_browser_model(cls) -> QStandardItemModel:
        """Create a data model from the modifiers structure."""
        ModifierService.load_modifiers_from_directory()
        _model = QStandardItemModel()
        _structure = ModifierRepository.get_structure()
        cls._append_structure(_model, _structure)
        return _model
    
    @classmethod
    def _append_structure(cls, parent: QStandardItem, _structure: dict):
        """Append sub structure to the model."""
        _repository = ModifierRepository.get_repository()
        for _key in _structure:
            _sub_structure = _structure[_key]
            if not isinstance(_sub_structure, dict):
                _name_id = _sub_structure
                _modifier_template = _repository[_name_id]
                _modifier_title = _modifier_template.get_title().title()
                _item = QStandardItem(_modifier_title)
                _item.setEditable(False)
                parent.appendRow(_item)
            else:
                _folder = QStandardItem(_key.title())
                _folder.setEditable(False)
                cls._append_structure(_folder, _sub_structure)
                parent.appendRow(_folder)