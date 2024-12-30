"""A set of services for modifier related GUI elements."""

from core.entities.layer import Layer
from core.services.modifier_service import ModifierService
from core.services.project_service import ProjectService
from gui.services.sequence_gui_service import SequenceGUIService
from utils.notification import Notification


class ModifierGUIService:
    """A set of services for modifier related GUI elements."""

    update_modifiers_signal = Notification()

    @classmethod
    def add_modifier_to_layer(cls,
                              sequence_id: int,
                              layer_id: int,
                              name_id: str):
        """Add a modifier to a layer."""
        _sequence = ProjectService.get_sequence_by_id(sequence_id)
        _modifier = ModifierService.modifier_from_template(name_id)
        _layer = _sequence.get_layer(layer_id)
        ModifierService.add_modifier_to_layer(_modifier, _layer)

        # TODO: Change this to a more precise signal:
        SequenceGUIService.update_sequence_signal.emit(sequence_id)
        cls.update_modifiers_signal.emit(sequence_id, layer_id)
