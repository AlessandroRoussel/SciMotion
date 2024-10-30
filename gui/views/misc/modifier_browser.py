"""
A panel for browsing through all the modifiers.

The ModifierBrowser panel provides the user with
a browser of all the modifiers loaded in the app.
"""

from pathlib import Path
from PySide6.QtWidgets import (QWidget, QTreeView)
from PySide6.QtGui import QStandardItem, QStandardItemModel

from core.entities.modifier_repository import ModifierRepository
from core.services.modifier_service import ModifierService


class ModifierBrowser(QTreeView):
    """A panel for browsing through all the modifiers."""

    _model: QStandardItemModel

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        ModifierService().load_modifiers_from_directory(Path("modifiers"))
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Modifiers"])
        _structure = ModifierRepository().get_structure()
        self.append_structure(self._model, _structure)
        self.setModel(self._model)
    
    def append_structure(self, parent: QStandardItem, _structure: dict):
        """Append sub structure to the model."""
        _repository = ModifierRepository().get_repository()
        for _key in _structure:
            _sub_structure = _structure[_key]
            if not isinstance(_sub_structure, dict):
                _name_id = _sub_structure
                _modifier_template = _repository[_name_id]
                _modifier_title = _modifier_template.get_title()
                parent.appendRow(QStandardItem(_modifier_title))
            else:
                _folder = QStandardItem(_key)
                self.append_structure(_folder, _sub_structure)
                parent.appendRow(_folder)