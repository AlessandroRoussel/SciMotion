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

    @staticmethod
    def adapt_layer_to_frame_rate(layer: Layer,
                                  old_frame_rate: float,
                                  new_frame_rate: float):
        """Adapt a layer start and end frames to a new frame rate."""
        _start_second = layer.get_start_frame() / old_frame_rate
        _end_second = layer.get_end_frame() / old_frame_rate
        _new_start_frame = round(_start_second * new_frame_rate)
        _new_end_frame = round(_end_second * new_frame_rate)
        layer.set_start_frame(_new_start_frame)
        layer.set_end_frame(_new_end_frame)
