"""An input for picking a color."""

from PySide6.QtWidgets import QPushButton, QWidget, QApplication
from PySide6.QtGui import (QPixmap, QPainter, QPainterPath, QRegion,
                           QBrush, QColor)
from PySide6.QtCore import Qt, QRectF

from data_types.color import Color
from utils.notification import Notification
from gui.views.dialogs.color_picker import ColorPicker


class ColorInput(QPushButton):
    """An input for picking a color."""

    _value: Color
    value_changed: Notification

    def __init__(self,
                 parent: QWidget = None,
                 value: Color = None):
        super().__init__(parent)
        self.value_changed = Notification()
        self._set_value(value if value is not None else Color.default())
        self.clicked.connect(self.open_dialog)
        self.setFixedSize(48, 24)
        self.setCursor(Qt.PointingHandCursor)
    
    def _set_value(self, value: Color):
        """Set the value stored by the input."""
        self._value = value
        self.value_changed.emit(self.get_value())
        self._update_display()
    
    def get_value(self) -> Color:
        """Return the value."""
        return self._value
    
    def _update_display(self):
        """Update the displayed color of the input."""
        # TODO : display a checkerboard for transparent colors
        _color = QApplication.palette().accent().color()
        _border_rgb = (
            f"rgb({_color.red()}, {_color.green()}, {_color.blue()})")
        self.setStyleSheet(
            f"""QPushButton, QPushButton:pressed, QPushButton:hover {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
            }}
            
            QPushButton:pressed, QPushButton:hover {{
                border: 1px solid {_border_rgb};
            }}""")
        self.update()

    def open_dialog(self):
        """Open the color picker."""
        _dialog = ColorPicker(self._value)
        if _dialog.exec():
            _color = _dialog.get_color()
            self._set_value(_color)
    
    def paintEvent(self, event):
        """Override to paint the color."""
        _painter = QPainter(self)
        _painter.setRenderHint(QPainter.Antialiasing)
        _rect = QRectF(self.rect())

        if self._value.get_value()[3] < 1:
            _painter.setBrush(QBrush(QColor.fromRgbF(.9, .9, .9)))
            _painter.setPen(Qt.NoPen)
            _painter.drawRoundedRect(_rect, 3, 3)

            _pixmap = QPixmap("checker.png")
            _path = QPainterPath()
            _rect2 = QRectF(_rect.left()+1, _rect.top()+1,
                            _rect.width()-2, _rect.height()-2)
            _path.addRoundedRect(_rect2, 3, 3)
            _painter.setClipPath(_path)
            _painter.setClipping(True)
            _painter.drawTiledPixmap(_rect, _pixmap)
            _painter.setClipping(False)
        
        _red, _green, _blue, _alpha = tuple(self._value.get_value())
        _painter.setBrush(QBrush(QColor.fromRgbF(_red, _green, _blue, _alpha)))
        _painter.setPen(Qt.NoPen)
        _painter.drawRoundedRect(_rect, 3, 3)

        super().paintEvent(event)