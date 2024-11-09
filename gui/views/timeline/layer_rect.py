"""The visual representation of a Layer in the TimelineView."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGraphicsRectItem, QWidget, QApplication,
                               QGraphicsSceneMouseEvent)
from PySide6.QtGui import QBrush, QPen, QPainter

from core.entities.layer import Layer
from utils.notification import Notification


class LayerRect(QGraphicsRectItem):
    """The visual representation of a Layer in the TimelineView."""

    _layer: Layer
    _brush: QBrush
    _selected_brush: QBrush
    _pen: QPen
    _selected: bool

    def __init__(self, layer: Layer):
        super().__init__()
        self._layer = layer
        self._brush = QBrush(QApplication.palette().light().color())
        self._selected_brush = QBrush(QApplication.palette().text().color())
        self._pen = Qt.NoPen
        self._selected = False
        self.setFlags(QGraphicsRectItem.ItemIsMovable)
    
    def set_rect(self, x: float, y: float, w: float, h: float):
        """Set the layer's rectangular area."""
        self.setRect(x, y, w, h)

    def get_frame_bounds(self) -> tuple[int, int]:
        """Return the start and end frame of the corresponding Layer."""
        return self._layer.get_start_frame(), self._layer.get_end_frame()

    def paint(self, qp: QPainter, option: Any, widget: QWidget = None):
        """Paint the item."""
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setBrush(self._selected_brush if self._selected else self._brush)
        qp.setPen(self._pen)
        qp.drawRect(self.rect())

    def select(self):
        """Select this layer."""
        self._selected = True
    
    def deselect(self):
        """De-select this layer."""
        self._selected = False