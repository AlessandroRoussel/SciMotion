"""The visual representation of a Layer in the TimelineView."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QGraphicsItem, QWidget, QApplication
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

from core.entities.layer import Layer


class LayerRect(QGraphicsItem):
    """The visual representation of a Layer in the TimelineView."""

    _layer: Layer
    _rect: QRectF
    _brush: QBrush
    _pen: QPen

    def __init__(self, layer: Layer):
        super().__init__()
        self._rect = (0, 0, 0, 0)
        self._layer = layer
        self._brush = QBrush(QApplication.palette().light().color())
        self._pen = Qt.NoPen
    
    def set_rect(self, x: float, y: float, w: float, h: float):
        """Set the layer's rectangular area."""
        self._rect = QRectF(x, y, w, h)

    def get_frame_bounds(self) -> tuple[int, int]:
        """Return the start and end frame of the corresponding Layer."""
        return self._layer.get_start_frame(), self._layer.get_end_frame()

    def boundingRect(self) -> QRectF:
        """Override the boundingRect method."""
        return self._rect

    def paint(self, qp: QPainter, option, widget: QWidget = None):
        """Paint the item."""
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setBrush(self._brush)
        qp.setPen(self._pen)
        qp.drawRect(self._rect)