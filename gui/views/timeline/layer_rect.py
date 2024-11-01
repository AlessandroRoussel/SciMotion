"""The visual representation of a Layer in the TimelineView."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtGui import QBrush, QColor

from core.entities.layer import Layer


class LayerRect(QGraphicsRectItem):
    """The visual representation of a Layer in the TimelineView."""

    _layer: Layer

    def __init__(self, layer: Layer):
        super().__init__(0, 0, 0, 0)
        self._layer = layer
        self.setBrush(QBrush(QColor(0,255,0)))
        self.setPen(Qt.NoPen)

    def get_frame_bounds(self) -> tuple[int, int]:
        """Return the start and end frame of the corresponding Layer."""
        return self._layer.get_start_frame(), self._layer.get_end_frame()