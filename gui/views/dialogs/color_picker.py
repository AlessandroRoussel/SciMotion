"""A color picker dialog."""

from enum import Enum

import numpy as np
from PySide6.QtGui import (QIcon, QLinearGradient, QBrush, QColor,
                           QPainter, QPen)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QSlider, QWidget,
                               QSizePolicy)

from utils.config import Config
from data_types.color import Color
from gui.services.dialog_service import DialogService


class ColorSliderType(Enum):
    """Enumerate all the color slider types."""

    HUE = 0
    SATURATION = 1
    VALUE = 2
    ALPHA = 3


class ColorPickerSlider(QSlider):
    """A color picker slider."""

    _type: ColorSliderType
    _style_color: Color

    def __init__(self, parent: QWidget, type: ColorSliderType):
        super().__init__(Qt.Horizontal, parent)
        self.setFixedHeight(20)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimum(0)
        self.setMaximum(65535)
        self.setSingleStep(1)
        self._type = type
        self._style_color = Color.default()
    
    def style_from_color(self, color: Color):
        """Style the slider according to a color."""
        self._style_color = color
        self.update()
    
    def get_value(self) -> float:
        """Get the slider's float value."""
        return self.value()/self.maximum()

    def paintEvent(self, event):
        """Override to paint a gradient on the slider."""
        _painter = QPainter(self)
        _painter.setRenderHint(QPainter.Antialiasing)

        _rect = self.rect()
        _radius = _rect.height()/2

        #TODO : Draw a checkerboard for the alpha slider

        # Draw the gradient:
        # TODO : implement my own static helper method for HSV <-> RGB
        _qcolor = QColor.fromRgbF(*self._style_color.get_value())
        _hue = _qcolor.hsvHueF()
        _sat = _qcolor.hsvSaturationF()
        _val = _qcolor.valueF()
        _gradient = QLinearGradient(0, 0, _rect.width(), 0)
        _gradient_resolution = 100
        _gradient_linspace = np.linspace(0, 1, _gradient_resolution)
        if self._type == ColorSliderType.HUE:
            for _i in _gradient_linspace:
                _gradient.setColorAt(_i, QColor.fromHsvF(_i%1, _sat, _val))
        elif self._type == ColorSliderType.SATURATION:
            for _i in _gradient_linspace:
                _gradient.setColorAt(_i, QColor.fromHsvF(_hue, _i, _val))
        elif self._type == ColorSliderType.VALUE:
            for _i in _gradient_linspace:
                _gradient.setColorAt(_i, QColor.fromHsvF(_hue, _sat, _i))
        elif self._type == ColorSliderType.ALPHA:
            for _i in _gradient_linspace:
                _gradient.setColorAt(_i, QColor.fromHsvF(_hue, _sat, _val, _i))
        _painter.setBrush(QBrush(_gradient))
        _painter.setPen(Qt.NoPen)
        _painter.drawRoundedRect(_rect, _radius, _radius)

        # Draw the handle:
        _thickness = 2
        _ratio = self.value()/self.maximum()
        _handle_x = _rect.left() + _ratio*(_rect.width()-2*_radius) + _radius
        _handle_y = _rect.top() + _radius

        _rad = _radius - _thickness/2 - 4
        _painter.setBrush(QBrush(QColor(0, 0, 0, 128)))
        _painter.setPen(QPen(QColor(255, 255, 255), _thickness))
        _painter.drawEllipse(QPointF(_handle_x, _handle_y), _rad, _rad)


class ColorPicker(QDialog):
    """A color picker dialog."""

    _color: Color
    _color_display: QWidget
    _hue_slider: ColorPickerSlider
    _sat_slider: ColorPickerSlider
    _val_slider: ColorPickerSlider
    _alpha_slider: ColorPickerSlider


    def __init__(self, color: Color = None):
        super().__init__()
        self._color = color if color is not None else Color.default()

        self.setWindowTitle("Color picker")
        self.setWindowIcon(QIcon(Config.app.icon))
        self.setFixedSize(QSize(250, 250))

        _layout = QVBoxLayout()
        _layout.setContentsMargins(8, 8, 8, 8)
        _layout.setSpacing(4)
        self.setFocusPolicy(Qt.ClickFocus)

        self._color_display = QWidget()
        self._color_display.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)
    
        _layout.addWidget(self._color_display)

        self._hue_slider = ColorPickerSlider(self, ColorSliderType.HUE)
        self._sat_slider = ColorPickerSlider(self, ColorSliderType.SATURATION)
        self._val_slider = ColorPickerSlider(self, ColorSliderType.VALUE)
        self._alpha_slider = ColorPickerSlider(self, ColorSliderType.ALPHA)

        _layout.addWidget(self._hue_slider)
        _layout.addWidget(self._sat_slider)
        _layout.addWidget(self._val_slider)
        _layout.addWidget(self._alpha_slider)

        self._hue_slider.valueChanged.connect(self._set_color_from_sliders)
        self._sat_slider.valueChanged.connect(self._set_color_from_sliders)
        self._val_slider.valueChanged.connect(self._set_color_from_sliders)
        self._alpha_slider.valueChanged.connect(self._set_color_from_sliders)
        self._set_sliders_from_color()

        DialogService.add_ok_cancel(self, _layout)
        self.setLayout(_layout)

    def _set_color_from_sliders(self):
        """React to changes in the sliders."""
        _hue = self._hue_slider.get_value()
        _sat = self._sat_slider.get_value()
        _val = self._val_slider.get_value()
        _alpha = self._alpha_slider.get_value()

        # TODO : implement my own static helper method for HSV <-> RGB
        _qcolor = QColor.fromHsvF(_hue%1, _sat, _val)
        _red = _qcolor.redF()
        _green = _qcolor.greenF()
        _blue = _qcolor.blueF()
        self._color = Color(_red, _green, _blue, _alpha)
        self._update_displayed_colors()
    
    def _set_sliders_from_color(self):
        """Set the sliders values from the current color."""
        # TODO : implement my own static helper method for HSV <-> RGB
        _qcolor = QColor.fromRgbF(*self._color.get_value())
        _hue = _qcolor.hsvHueF()
        _sat = _qcolor.hsvSaturationF()
        _val = _qcolor.valueF()
        _alpha = _qcolor.alphaF()
        self._hue_slider.setValue(int(round(self._hue_slider.maximum()*_hue)))
        self._sat_slider.setValue(int(round(self._sat_slider.maximum()*_sat)))
        self._val_slider.setValue(int(round(self._val_slider.maximum()*_val)))
        self._alpha_slider.setValue(int(round(self._alpha_slider.maximum()*_alpha)))

    def _update_displayed_colors(self):
        """Change the sliders styles according to the chosen color."""
        _qcolor = QColor.fromRgbF(*self._color.get_value())
        _red = _qcolor.red()
        _green = _qcolor.green()
        _blue = _qcolor.blue()
        _alpha = _qcolor.alphaF()
        self._color_display.setStyleSheet(
            f"background-color: rgba({_red}, {_green}, {_blue}, {_alpha});")

        self._hue_slider.style_from_color(self._color)
        self._sat_slider.style_from_color(self._color)
        self._val_slider.style_from_color(self._color)
        self._alpha_slider.style_from_color(self._color)

    def get_color(self) -> Color:
        """Return the selected color."""
        return self._color