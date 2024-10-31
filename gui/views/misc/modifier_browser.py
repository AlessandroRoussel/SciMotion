"""
A panel for browsing through all the modifiers.

The ModifierBrowser panel provides the user with
a browser of all the modifiers loaded in the app.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTreeView)
from PySide6.QtGui import QStandardItemModel

from gui.services.modifier_gui_service import ModifierGUIService


class ModifierBrowser(QTreeView):
    """A panel for browsing through all the modifiers."""

    _model: QStandardItemModel

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._model = ModifierGUIService.create_browser_model()
        self._model.setHorizontalHeaderLabels(["Modifiers"])
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setModel(self._model)
