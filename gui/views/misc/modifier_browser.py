"""
A panel for browsing through all the modifiers.

The ModifierBrowser panel provides the user with
a browser of all the modifiers loaded in the app.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTreeView)
from PySide6.QtGui import QStandardItem, QStandardItemModel

from core.entities.modifier_repository import ModifierRepository
from core.services.modifier_service import ModifierService


class ModifierBrowser(QTreeView):
    """A panel for browsing through all the modifiers."""

    _model: QStandardItemModel

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._create_browser_model()
        self._model.setHorizontalHeaderLabels(["Modifiers"])
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setModel(self._model)

    def _create_browser_model(self):
        """Create a data model from the modifiers structure."""
        ModifierService.load_modifiers_from_directory()
        self._model = QStandardItemModel()
        _structure = ModifierRepository.get_structure()
        self._append_structure_to(_structure, self._model)
    
    def _append_structure_to(self, _structure: dict, parent: QStandardItem):
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
                self._append_structure_to(_sub_structure, _folder)
                parent.appendRow(_folder)