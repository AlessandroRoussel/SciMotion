"""A set of services for layer related GUI elements."""

from core.entities.layer import Layer
from core.services.modifier_service import ModifierService
from utils.notification import Notification


class LayerGUIService:
    """A set of services for layer related GUI elements."""

    focus_layer_signal = Notification()
    _focused_layer: Layer = None

    @staticmethod
    def add_modifier_to_layer(layer: Layer, name_id: str):
        """Add a modifier to a layer."""
        _modifier = ModifierService.modifier_from_template(name_id)
        ModifierService.add_modifier_to_layer(_modifier, layer)
    
    @classmethod
    def focus_layer(cls, layer: Layer):
        """Set which layer is currently focused."""
        cls._focused_layer = layer
        cls.focus_layer_signal.emit(layer)
    
    @classmethod
    def get_focused_layer(cls) -> Layer:
        """Return the focused layer."""
        if cls._focused_layer is None:
            return None
        return cls._focused_layer
