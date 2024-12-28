"""
A panel for listing the modifiers of a layer.

The ModifierList panel provides the user with
a list of all the modifiers of a layer.
"""

from PySide6.QtWidgets import (QWidget, QToolBox)

from core.entities.layer import Layer
from gui.services.layer_gui_service import LayerGUIService
from gui.views.misc.modifier_editor import ModifierEditor


class ModifierList(QToolBox):
    """A panel for listing the modifiers of a layer."""

    _layer: Layer

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._layer = None
        LayerGUIService.focus_layer_signal.connect(self.focus_layer)
    
    def focus_layer(self, layer: Layer):
        """Change currently focused layer."""
        if self._layer is layer:
            return
        self._layer = layer
        self.rebuild()
    
    def rebuild(self):
        """Build widget content based on focused layer."""
        while self.count() > 0:
            self.removeItem(0)
        if self._layer is None or not isinstance(self._layer, Layer):
            return
        _modifier_list = self._layer.get_modifier_list()
        for _modifier in _modifier_list:
            _editor = ModifierEditor(self, _modifier)
            self.addItem(_editor, _editor.get_title())