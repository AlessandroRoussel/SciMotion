"""A set of services for sequence related GUI elements."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from core.entities.project import Project
from gui.views.dialogs.sequence_dialog import SequenceDialog
from core.services.project_service import ProjectService
from core.services.render_service import RenderService
from core.entities.sequence import Sequence
from utils.notification import Notification
from utils.time import Time
from utils.image import Image


class SequenceGUIService():
    """A set of services for sequence related GUI elements."""

    create_sequence_signal = Notification()
    open_sequence_signal = Notification()

    @classmethod
    def create_new_sequence(cls):
        """Create a new sequence."""
        _dialog = SequenceDialog()
        if _dialog.exec():
            (_title, _width, _height,
             _frame_rate, _duration) = _dialog.get_values()
            _sequence = Sequence(_title, _width, _height,
                                 _duration, _frame_rate)
            _id = ProjectService.add_sequence_to_project(_sequence)
            cls.create_sequence_signal.emit(_id)
            cls.open_sequence_signal.emit(_id)

    @classmethod
    def create_browser_model(cls) -> QStandardItemModel:
        """Create a data model from the sequence browser."""
        _model = QStandardItemModel()
        _sequences = Project.get_sequence_dict()
        for _sequence_id in _sequences:
            _sequence = _sequences[_sequence_id]
            cls.add_sequence_to_model(_model, _sequence, _sequence_id)
        return _model
    
    @staticmethod
    def add_sequence_to_model(model: QStandardItemModel,
                              sequence: Sequence,
                              sequence_id: int):
        """Add a sequence to a browser data model."""
        _title = sequence.get_title()
        _dimensions = f"{sequence.get_width()}x{sequence.get_height()}px"
        _fps = sequence.get_frame_rate()
        _duration = Time.format_time(sequence.get_duration(), _fps)
        _frame_rate = f"{_fps}f/s"

        _item_title = QStandardItem(_title)
        _item_dimensions = QStandardItem(_dimensions)
        _item_duration = QStandardItem(_duration)
        _item_frame_rate = QStandardItem(_frame_rate)

        _item_title.setData(sequence_id, Qt.UserRole)
        _item_dimensions.setData(sequence_id, Qt.UserRole)
        _item_duration.setData(sequence_id, Qt.UserRole)
        _item_frame_rate.setData(sequence_id, Qt.UserRole)

        _item_title.setEditable(False)
        _item_dimensions.setEditable(False)
        _item_duration.setEditable(False)
        _item_frame_rate.setEditable(False)

        model.appendRow([_item_title,
                         _item_dimensions,
                         _item_duration,
                         _item_frame_rate])
    
    @staticmethod
    def request_image_from_sequence(sequence_id: int, frame: int) -> Image:
        """Return a rendered frame within a sequence."""
        _sequence = Project.get_sequence_dict()[sequence_id]
        _image = RenderService.render_sequence_frame(_sequence)
        return _image