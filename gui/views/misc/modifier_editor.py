"""
A panel for editing the parameters of a modifier.

The ModifierEditor panel provides the user with
an editor for all the parameters of a modifier.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGridLayout, QLabel,
                               QSizePolicy, QFrame)

from core.entities.modifier import Modifier
from core.entities.parameter import Parameter
from core.entities.modifier_repository import ModifierRepository
from data_types.data_type import DataType
from utils.notification import Notification
from gui.services.input_gui_service import InputGUIService


class ModifierEditor(QFrame):
    """A panel for editing the parameters of a modifier."""

    _title: str
    _sequence_id: int
    _layer_id: int

    def __init__(self,
                 parent: QWidget,
                 modifier: Modifier,
                 sequence_id: int,
                 layer_id: int):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self._sequence_id = sequence_id
        self._layer_id = layer_id
        self.build_from_modifier(modifier)
    
    def build_from_modifier(self, modifier: Modifier):
        """Build GUI from modifier template and data."""
        _template_id = modifier.get_template_id()
        _param_list = modifier.get_parameter_list()
        _template = ModifierRepository.get_template(_template_id)
        self._title = _template.get_title()

        _layout = QGridLayout(self)
        _layout.setAlignment(Qt.AlignLeft)
        self.setLayout(_layout)

        _title_widget = QLabel(self._title, self)
        _layout.addWidget(_title_widget, 0, 0, 1, 2)

        _param_template_list = _template.get_parameter_template_list()
        for _i in range(len(_param_template_list)):
            _param = _param_list[_i]
            _param_template = _param_template_list[_i]

            _input = InputGUIService.input_from_parameter(
                self,
                _param_template,
                _param,
                self._sequence_id,
                self._layer_id)
            
            if _input is None:
                continue
            _param_title = _param_template.get_title()
            _label = QLabel(f"{_param_title}:", self)
            _layout.addWidget(_label, _i+1, 0)
            _layout.addWidget(_input, _i+1, 1)
    
    def get_title(self) -> str:
        """Get modifier title."""
        return self._title
