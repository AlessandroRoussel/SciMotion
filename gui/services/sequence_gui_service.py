"""A set of services for sequence related GUI elements."""

import moderngl

from core.services.layer_service import LayerService
from gui.views.dialogs.sequence_dialog import SequenceDialog
from gui.views.dialogs.solid_layer_dialog import SolidLayerDialog
from core.services.project_service import ProjectService
from core.services.render_service import RenderService
from core.services.animation_service import AnimationService
from core.services.modifier_service import ModifierService
from core.entities.solid_layer import SolidLayer
from core.entities.keyframe import Keyframe, KeyframeType
from core.entities.sequence import Sequence
from utils.notification import Notification
from data_types.number import Number
from data_types.vector2 import Vector2
from data_types.color import Color
from utils.image import Image


class SequenceGUIService:
    """A set of services for sequence related GUI elements."""

    create_sequence_signal = Notification()
    open_sequence_signal = Notification()
    update_sequence_signal = Notification()
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
    
    @classmethod
    def open_sequence_parameters(cls):
        """Open the parameters for the currently focused sequence."""
        if cls._focused_sequence is None:
            return
        _sequence = cls.get_focused_sequence()
        _dialog = SequenceDialog(_sequence)
        if _dialog.exec():
            (_title, _width, _height,
             _frame_rate, _duration) = _dialog.get_values()
            for _layer in _sequence.get_layer_list():
                LayerService.adapt_layer_to_frame_rate(
                    _layer, _sequence.get_frame_rate(), _frame_rate)
            _sequence.set_title(_title)
            _sequence.set_width(_width)
            _sequence.set_height(_height)
            _sequence.set_frame_rate(_frame_rate)
            _sequence.set_duration(_duration)
            cls.update_sequence_signal.emit(cls._focused_sequence)
    
    @staticmethod
    def request_texture_from_sequence(sequence_id: int,
                                      frame: int
                                      ) -> moderngl.Texture:
        """Return a rendered frame within a sequence."""
        # TODO : Optimize a lot this part, render only if needed
        # (probably better to do it in the core package,
        # with a MemoryStorage class for instance)
        _sequence = ProjectService.get_sequence_by_id(sequence_id)
        _texture = RenderService.render_sequence_frame(_sequence, frame)
        return _texture

    @classmethod
    def focus_sequence(cls, sequence_id: int=None):
        """Set which sequence is currently focused."""
        cls._focused_sequence = sequence_id
        cls.focus_sequence_signal.emit(sequence_id)

    @classmethod
    def offset_current_frame(cls, offset: int):
        """Offset the current frame of the focused sequence."""
        # TODO : store the current frames in this class instead,
        # and make sure to trim the frame between 0 and max_frame
        if cls._focused_sequence is not None:
            cls.offset_current_frame_signal.emit(cls._focused_sequence, offset)

    @classmethod
    def set_current_frame(cls, frame: int):
        """Set the current frame of the focused sequence."""
        if cls._focused_sequence is not None:
            _max_frame = cls.get_focused_sequence().get_duration()-1
            _frame = max(0, min(_max_frame, frame))
            cls.set_current_frame_signal.emit(cls._focused_sequence, _frame)
    
    @classmethod
    def create_new_solid_layer(cls):
        """Create a new solid layer."""
        if cls._focused_sequence is None:
            return
        _dialog = SolidLayerDialog(cls.get_focused_sequence())
        if _dialog.exec():
            (_title, _width, _height, _color) = _dialog.get_values()
            _seq = ProjectService.get_sequence_by_id(cls._focused_sequence)
            _start_frame = 0
            _end_frame = _seq.get_duration()
            _layer = SolidLayer(_title, _start_frame, _end_frame,
                                _width, _height, _color)
            LayerService.add_layer_to_sequence(_layer, _seq)
            cls.update_sequence_signal.emit(cls._focused_sequence)
    
    @classmethod
    def get_focused_sequence(cls) -> Sequence:
        """Return the focused sequence."""
        if cls._focused_sequence is None:
            return None
        return ProjectService.get_sequence_by_id(cls._focused_sequence)
