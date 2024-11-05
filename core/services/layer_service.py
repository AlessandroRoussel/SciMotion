"""
Service concerning layers in general.

The LayerService class defines services within the core
package, concerning layers that the user can stack within
a Sequence. This includes adding or removing layers...
"""

from core.entities.layer import Layer
from core.entities.sequence import Sequence


class LayerService:
    """Service concerning layers in general."""

    @staticmethod
    def add_layer_to_sequence(layer: Layer, sequence: Sequence):
        """Add a Layer to a Sequence."""
        _layer_list = sequence.get_layer_list()
        _layer_list.append(layer)
