"""
A panel for editing the properties of a layer.

The LayerPropertiesPanel panel provides the user
with an editor for all the properties of a layer.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QFrame, QGridLayout,
                               QLabel, QSizePolicy)

from core.services.project_service import ProjectService
from gui.services.sequence_gui_service import SequenceGUIService
from gui.services.input_gui_service import InputGUIService
from utils.config import Config


class LayerPropertiesPanel(QFrame):
    """A panel for editing the properties of a layer."""

    _layout: QGridLayout
    _sequence_id: int
    _layer_id: int

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._sequence_id = None
        self._layer_id = None

        self.setFrameStyle(QFrame.NoFrame)

        _margin = Config.modifier_editor.margin
        self._layout = QGridLayout(self)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(_margin)
        self._layout.setContentsMargins(_margin, _margin, _margin, _margin)
        self.setLayout(self._layout)

        SequenceGUIService.update_selected_layers_signal.connect(
            self.update_selected_layers)
        SequenceGUIService.focus_sequence_signal.connect(
            self.focus_sequence)
    
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
        _properties_templates = _layer.get_properties_templates()

        _title_widget = QLabel(_layer.get_title(), self)
        self._layout.addWidget(_title_widget, 0, 0, 1, 2)

        _row = 1
        for _name_id, _property_template in _properties_templates.items():
            if not _property_template.get_accepts_keyframes():
                continue
            _property = _layer.get_property_parameter(_name_id)
            _input = InputGUIService.input_from_parameter(
                self,
                _property_template,
                _property,
                self._sequence_id,
                self._layer_id)
            if _input is None:
                continue
            self._layout.addWidget(_input)
            _property_title = _property_template.get_title()
            self._layout.addWidget(QLabel(f"{_property_title}:", self),
                                   _row, 0)
            self._layout.addWidget(_input, _row, 1)
            _row += 1
