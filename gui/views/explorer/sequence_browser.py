"""
A panel for browsing sequences within the project.

The SequenceBrowser panel provides the user with
a browser of all the sequences in the project.
"""

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import (QWidget, QTreeView, QHeaderView)
from PySide6.QtGui import QStandardItemModel

from core.entities.project import Project
from gui.services.sequence_gui_service import SequenceGUIService


class SequenceBrowser(QTreeView):
    """A panel for browsing sequences within the project."""

    _model: QStandardItemModel

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._model = SequenceGUIService.create_browser_model()
        self._model.setHorizontalHeaderLabels(["Sequences",
                                               "Dimensions",
                                               "Duration",
                                               "Frame rate"])
        self.header().setSectionResizeMode(QHeaderView.Interactive)
        self.header().setCascadingSectionResizes(True)
        self.setModel(self._model)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        SequenceGUIService.create_sequence_signal.connect(
            self.create_sequence)
        self.doubleClicked.connect(self.on_sequence_double_clicked)
    
    def create_sequence(self, sequence_id: int):
        """Create a sequence in the model."""
        _sequences = Project.get_sequence_dict()
        _sequence = _sequences[sequence_id]
        SequenceGUIService.add_sequence_to_model(
            self._model, _sequence, sequence_id)

    def on_sequence_double_clicked(self, index: QModelIndex):
        """Handle double clicking on a sequence."""
        _sequence_id = self._model.data(index, Qt.UserRole)
        SequenceGUIService.open_sequence_signal.emit(_sequence_id)
