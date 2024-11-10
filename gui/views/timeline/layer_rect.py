"""The visual representation of a Layer in the TimelineView."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGraphicsRectItem, QApplication,
                               QGraphicsSceneDragDropEvent)
from PySide6.QtGui import QBrush

from core.entities.layer import Layer
from gui.services.layer_gui_service import LayerGUIService
from gui.services.sequence_gui_service import SequenceGUIService


class LayerRect(QGraphicsRectItem):
    """The visual representation of a Layer in the TimelineView."""

    _layer: Layer
    _sequence_id: int
    _selected: bool

    def __init__(self, layer: Layer, sequence_id: int):
        super().__init__()
        self._layer = layer
        self._sequence_id = sequence_id
        self._selected = False
        self.setPen(Qt.NoPen)
        self.deselect()
        self.setAcceptDrops(True)
    
    def set_rect(self, x: float, y: float, w: float, h: float):
        """Set the layer's rectangular area."""
        self.setRect(x, y, w, h)

    def get_frame_bounds(self) -> tuple[int, int]:
        """Return the start and end frame of the corresponding Layer."""
        return self._layer.get_start_frame(), self._layer.get_end_frame()

    def select(self):
        """Select this layer."""
        self.setBrush(QBrush(QApplication.palette().text().color()))
    
    def deselect(self):
        """De-select this layer."""
        self.setBrush(QBrush(QApplication.palette().light().color()))

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        """Handle the drag entering the item."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setBrush(QBrush(QApplication.palette().accent().color()))

    def dragLeaveEvent(self, event: QGraphicsSceneDragDropEvent):
        """Reset visual feedback when drag leaves the item."""
        if self._selected:
            self.select()
        else:
            self.deselect()

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):
        """Handle the drop event."""
        if event.mimeData().hasText():
            _name_id = event.mimeData().text()
            LayerGUIService.add_modifier_to_layer(self._layer, _name_id)
            SequenceGUIService.update_sequence_signal.emit(self._sequence_id)
            event.acceptProposedAction()