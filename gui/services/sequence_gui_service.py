"""A set of services for sequence related GUI elements."""

from core.entities.project import Project
from gui.views.dialogs.sequence_dialog import SequenceDialog
from core.services.project_service import ProjectService
from core.services.render_service import RenderService
from core.entities.sequence import Sequence
from utils.notification import Notification
from utils.image import Image


class SequenceGUIService:
    """A set of services for sequence related GUI elements."""

    create_sequence_signal = Notification()
    open_sequence_signal = Notification()
    close_sequence_signal = Notification()
    focus_sequence_signal = Notification()
    offset_current_frame_signal = Notification()
    set_current_frame_signal = Notification()

    _focused_sequence: int = None

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
    
    @staticmethod
    def request_image_from_sequence(sequence_id: int, frame: int) -> Image:
        """Return a rendered frame within a sequence."""
        _sequence = Project.get_sequence_dict()[sequence_id]
        _image = RenderService.render_sequence_frame(_sequence)
        return _image

    @classmethod
    def focus_sequence(cls, sequence_id: int=None):
        """Set which sequence is currently focused."""
        cls._focused_sequence = sequence_id
        cls.focus_sequence_signal.emit(sequence_id)

    @classmethod
    def offset_current_frame(cls, offset: int):
        """Offset the current frame of the focused sequence."""
        if cls._focused_sequence is not None:
            cls.offset_current_frame_signal.emit(cls._focused_sequence, offset)

    @classmethod
    def set_current_frame(cls, frame: int):
        """Set the current frame of the focused sequence."""
        if cls._focused_sequence is not None:
            cls.set_current_frame_signal.emit(cls._focused_sequence, frame)
