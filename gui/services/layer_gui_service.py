"""A set of services for layer related GUI elements."""

from core.entities.layer import Layer
from core.services.modifier_service import ModifierService


class LayerGUIService:
    """A set of services for layer related GUI elements."""

    @staticmethod
    def add_modifier_to_layer(layer: Layer, name_id: str):
        """Add a modifier to a layer."""
        _modifier = ModifierService.modifier_from_template(name_id)
        ModifierService.add_modifier_to_layer(_modifier, layer)