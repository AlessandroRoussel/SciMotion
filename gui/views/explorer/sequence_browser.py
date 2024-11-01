"""
A panel for browsing sequences within the project.

The SequenceBrowser panel provides the user with
a browser of all the sequences in the project.
"""

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import (QWidget, QTreeView, QHeaderView)
from PySide6.QtGui import QStandardItem, QStandardItemModel, QCursor

from core.entities.project import Project
from gui.services.sequence_gui_service import SequenceGUIService
from core.entities.sequence import Sequence
from utils.time import Time


class SequenceBrowser(QTreeView):
    """A panel for browsing sequences within the project."""

    _model: QStandardItemModel

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._create_browser_model()
        self._model.setHorizontalHeaderLabels(["Sequences",
                                               "Dimensions",
                                               "Duration",
                                               "Frame rate"])
        self.header().setSectionResizeMode(QHeaderView.Interactive)
        self.header().setCascadingSectionResizes(True)
        self.setModel(self._model)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSortingEnabled(True)
        SequenceGUIService.create_sequence_signal.connect(
            self.create_sequence)
        self.doubleClicked.connect(self.on_sequence_double_clicked)
    
    def create_sequence(self, sequence_id: int):
        """Create a sequence in the model."""
        _sequences = Project.get_sequence_dict()
        _sequence = _sequences[sequence_id]
        self._add_sequence_to_model(_sequence, sequence_id)

    def on_sequence_double_clicked(self, index: QModelIndex):
        """Handle double clicking on a sequence."""
        _sequence_id = self._model.data(index, Qt.UserRole)
        SequenceGUIService.open_sequence_signal.emit(_sequence_id)

    def _create_browser_model(self):
        """Create a data model from the sequence browser."""
        self._model = QStandardItemModel()
        _sequences = Project.get_sequence_dict()
        for _sequence_id in _sequences:
            _sequence = _sequences[_sequence_id]
            self._add_sequence_to_model(_sequence, _sequence_id)

    def _add_sequence_to_model(self,
                               sequence: Sequence,
                               sequence_id: int):
        """Add a sequence to a browser data model."""
        _items = []
        _texts = []

        _texts.append(sequence.get_title())
        _texts.append(f"{sequence.get_width()}x{sequence.get_height()}px")
        _fps = sequence.get_frame_rate()
        _texts.append(Time.format_time(sequence.get_duration(), _fps))
        _texts.append(f"{_fps}f/s")

        for _text in _texts:
            _items.append(QStandardItem(_text))

        for _item in _items:
            _item.setData(sequence_id, Qt.UserRole)
            _item.setEditable(False)

        self._model.appendRow(_items)
