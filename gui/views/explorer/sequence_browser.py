"""
A panel for browsing sequences within the project.

The SequenceBrowser panel provides the user with
a browser of all the sequences in the project.
"""

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import (QWidget, QTreeView, QHeaderView)
from PySide6.QtGui import QStandardItem, QStandardItemModel, QCursor

from core.entities.project import Project
from core.services.project_service import ProjectService
from gui.services.sequence_gui_service import SequenceGUIService
from core.entities.sequence import Sequence
from utils.time import Time


class SequenceBrowser(QTreeView):
    """A panel for browsing sequences within the project."""

    _sequence_rows: dict[int, list[QStandardItem]]
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
        SequenceGUIService.create_sequence_signal.connect(self.create_sequence)
        SequenceGUIService.update_sequence_signal.connect(self.update_sequence)
        self.doubleClicked.connect(self.on_sequence_double_clicked)
    
    def create_sequence(self, sequence_id: int):
        """Create a sequence in the model."""
        self._add_sequence_to_model(sequence_id)
    
    def update_sequence(self, sequence_id: int):
        """Update a sequence in the model."""
        _new_values = self._get_row_values_from_sequence(sequence_id)
        for _i in range(len(_new_values)):
            _item = self._sequence_rows[sequence_id][_i]
            _new_value = _new_values[_i]
            _item.setText(_new_value)

    def on_sequence_double_clicked(self, index: QModelIndex):
        """Handle double clicking on a sequence."""
        _sequence_id = self._model.data(index, Qt.UserRole)
        SequenceGUIService.open_sequence_signal.emit(_sequence_id)

    def _create_browser_model(self):
        """Create a data model from the sequence browser."""
        self._sequence_rows = dict()
        self._model = QStandardItemModel()
        _sequences = Project.get_sequence_dict()
        for _sequence_id in _sequences:
            self._add_sequence_to_model(_sequence_id)

    def _get_row_values_from_sequence(self, sequence_id: id) -> list[str]:
        """Return the values to display from a sequence."""
        _sequence = ProjectService.get_sequence_by_id(sequence_id)
        _texts = []
        _texts.append(_sequence.get_title())
        _texts.append(f"{_sequence.get_width()}x{_sequence.get_height()}px")
        _fps = _sequence.get_frame_rate()
        _texts.append(Time.format_time(_sequence.get_duration(), _fps))
        _texts.append(f"{_fps}f/s")
        return _texts

    def _add_sequence_to_model(self, sequence_id: int):
        """Add a sequence to a browser data model."""
        _items = []
        for _text in self._get_row_values_from_sequence(sequence_id):
            _items.append(QStandardItem(_text))

        for _item in _items:
            _item.setData(sequence_id, Qt.UserRole)
            _item.setEditable(False)

        self._sequence_rows[sequence_id] = _items
        self._model.appendRow(_items)
