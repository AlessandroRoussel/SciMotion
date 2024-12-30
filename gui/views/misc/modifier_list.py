"""
A panel for listing the modifiers of a layer.

The ModifierList panel provides the user with
a list of all the modifiers of a layer.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame,
                               QSizePolicy)

from core.services.project_service import ProjectService
from gui.services.sequence_gui_service import SequenceGUIService
from gui.services.modifier_gui_service import ModifierGUIService
from gui.views.misc.modifier_editor import ModifierEditor
from utils.config import Config


class ModifierList(QScrollArea):
    """A panel for listing the modifiers of a layer."""

    _layout: QVBoxLayout
    _sequence_id: int
    _layer_id: int

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._sequence_id = None
        self._layer_id = None

        _widget = QWidget(self)
        self.setWidget(_widget)
        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        
        _margin = Config.modifier_editor.margin
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(_margin)
        self._layout.setContentsMargins(_margin, _margin, _margin, _margin)
        _widget.setLayout(self._layout)

        SequenceGUIService.update_selected_layers_signal.connect(
            self.update_selected_layers)
        SequenceGUIService.focus_sequence_signal.connect(
            self.focus_sequence)
        ModifierGUIService.update_modifiers_signal.connect(
            self.update_modifiers)
    
    def rebuild(self):
        """Build widget content based on focused layer."""
        while self._layout.count():
            _item = self._layout.takeAt(0)
            _widget = _item.widget()
            if _widget is not None:
                _widget.deleteLater()
            else:
                self._layout.removeItem(_item)
        if self._sequence_id is None or self._layer_id is None:
            return
        _sequence = ProjectService.get_sequence_by_id(self._sequence_id)
        _layer = _sequence.get_layer(self._layer_id)
        _modifier_list = _layer.get_modifier_list()
        for _modifier in _modifier_list:
            _editor = ModifierEditor(self, _modifier)
            self._layout.addWidget(_editor)
        self._layout.addStretch()
    
    def update_selected_layers(self, sequence_id: int):
        """Handle changing which layers are selected in a sequence."""
        if sequence_id != self._sequence_id:
            return
        _layer_id = SequenceGUIService.get_focused_layer(sequence_id)
        if self._layer_id == _layer_id:
            return
        self._layer_id = _layer_id
        self.rebuild()
    
    def focus_sequence(self, sequence_id: int):
        """Handle which sequence is focused."""
        _layer_id = SequenceGUIService.get_focused_layer(sequence_id)
        if self._sequence_id == sequence_id and self._layer_id == _layer_id:
            return
        self._sequence_id = sequence_id
        self._layer_id = _layer_id
        self.rebuild()
    
    def update_modifiers(self, sequence_id: int, layer_id: int):
        """Handle adding / removing modifiers from a layer."""
        if sequence_id != self._sequence_id or layer_id != self._layer_id:
            return
        self.rebuild()
