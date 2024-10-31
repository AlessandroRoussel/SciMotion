"""
A pane for viewing images and video sequences.

The ViewerPane inherits from QTabWidget and provides the user with
a tabbed pane for viewing sequences and media. It holds ViewerTab
objects which can display media or sequences.
"""

from PySide6.QtWidgets import (QTabWidget, QWidget)

from gui.views.viewer.viewer_tab import ViewerTab
from core.entities.project import Project
from gui.services.sequence_gui_service import SequenceGUIService
from core.entities.sequence import Sequence
from core.entities.solid_layer import SolidLayer
from core.services.render_service import RenderService
from core.services.layer_service import LayerService
from core.services.modifier_service import ModifierService
from data_types.color import Color
from gui.views.viewer.gl_viewer import GLViewer


class ViewerPane(QTabWidget):
    """A pane for viewing images and video sequences."""

    _tabs: dict[int, int]  # dict(tab id => sequence id)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._tabs = dict()
        SequenceGUIService.open_sequence_signal.connect(self.open_sequence)

    def open_sequence(self, sequence_id: int):
        """Open a tab for viewing a sequence in the project."""
        if sequence_id in self._tabs.values():
            _tab_id = list(self._tabs.keys())[
                list(self._tabs.values()).index(sequence_id)]
            self.setCurrentIndex(_tab_id)
            return
        _sequence = Project.get_sequence_dict()[sequence_id]
        _viewer_tab = ViewerTab(self, sequence_id)
        self.addTab(_viewer_tab, _sequence.get_title())
        _tab_id = self.count()-1
        self._tabs[_tab_id] = sequence_id
        self.setCurrentIndex(_tab_id)