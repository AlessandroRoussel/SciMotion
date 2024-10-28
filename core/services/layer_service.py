"""
Service concerning layers in general.

The LayerService class defines services within the core
package, concerning layers that the user can stack within
a Sequence. This includes adding or removing layers...
"""

from utils.singleton import Singleton
from core.entities.layer import Layer
from core.entities.sequence import Sequence


class LayerService(metaclass=Singleton):
    """Service concerning layers in general."""

    def __init__(self):
        # TODO : load configuration if needed
        pass

    def add_layer_to_sequence(self, layer: Layer, sequence: Sequence):
        """Add a Layer to a Sequence."""
        _layer_list = sequence.get_layer_list()
        _layer_list.append(layer)
