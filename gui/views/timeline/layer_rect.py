"""The visual representation of a Layer in the TimelineView."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGraphicsRectItem, QApplication,
                               QGraphicsSceneDragDropEvent)
from PySide6.QtGui import QBrush

from core.entities.layer import Layer
from core.services.project_service import ProjectService
from gui.services.modifier_gui_service import ModifierGUIService
from gui.services.sequence_gui_service import SequenceGUIService


class LayerRect(QGraphicsRectItem):
    """The visual representation of a Layer in the TimelineView."""

    _layer_id: int
    _sequence_id: int
    _frame_bounds: tuple[int, int]

    def __init__(self, layer_id: int, sequence_id: int):
        super().__init__()
        self._layer_id = layer_id
        self._sequence_id = sequence_id
        _layer = ProjectService.get_sequence_by_id(
            sequence_id).get_layer(layer_id)
        self._frame_bounds = (_layer.get_start_frame(),
                              _layer.get_end_frame())
        self.setPen(Qt.NoPen)
        self.setAcceptDrops(True)
        self.update_selection_status()
    
    def set_rect(self, x: float, y: float, w: float, h: float):
        """Set the layer's rectangular area."""
        self.setRect(x, y, w, h)

    def get_layer_id(self) -> int:
        """Get represented layer's index."""
        return self._layer_id

    def get_frame_bounds(self) -> tuple[int, int]:
        """Return the start and end frame of the corresponding Layer."""
        return self._frame_bounds

    def update_selection_status(self):
        """Update the visual display of selection status for this layer."""
        if SequenceGUIService.is_layer_selected(
            self._sequence_id, self._layer_id):
            self.setBrush(QBrush(QApplication.palette().text().color()))
        else:
            self.setBrush(QBrush(QApplication.palette().light().color()))

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        """Handle the drag entering the item."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setBrush(QBrush(QApplication.palette().accent().color()))

    def dragLeaveEvent(self, event: QGraphicsSceneDragDropEvent):
        """Reset visual feedback when drag leaves the item."""
        self.update_selection_status()

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):
        """Handle the drop event."""
        if event.mimeData().hasText():
            _name_id = event.mimeData().text()
            ModifierGUIService.add_modifier_to_layer(
                self._sequence_id, self._layer_id, _name_id)
            event.acceptProposedAction()