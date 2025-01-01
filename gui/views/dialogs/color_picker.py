"""A color picker dialog."""

from enum import Enum

import numpy as np
import moderngl
from PySide6.QtGui import (QIcon, QLinearGradient, QBrush, QColor,
                           QPainter, QPainterPath, QPixmap, QPen, QRegion)
from PySide6.QtCore import Qt, QSize, QPointF, QRectF
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QSlider, QWidget,
                               QSizePolicy, QHBoxLayout, QGridLayout,
                               QLabel)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from utils.config import Config
from data_types.color import Color
from gui.services.dialog_service import DialogService


class ColorSliderType(Enum):
    """Enumerate all the color slider types."""

    RED = 0
    GREEN = 1
    BLUE = 2
    ALPHA = 3
    HUE = 4
    SATURATION = 5
    LIGHTNESS = 6


class ColorPickerSlider(QSlider):
    """A color picker slider."""

    _type: ColorSliderType
    _style_color: Color

    def __init__(self, parent: QWidget, type: ColorSliderType):
        super().__init__(Qt.Horizontal, parent)
        self.setFixedHeight(14)
        self.setMinimum(0)
        self.setMaximum(65535)
        self.setSingleStep(1)
        self._type = type
        self._style_color = Color.default()
        self.setCursor(Qt.PointingHandCursor)
    
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

        _rect = QRectF(self.rect())
        _margin = 8

        if self._type == ColorSliderType.ALPHA:
            _painter.setBrush(QColor.fromRgbF(.9, .9, .9))
            _painter.setPen(Qt.NoPen)
            _rect2 = QRectF(_rect.left(), _rect.top(),
                            _rect.width()-1, _rect.height())
            _painter.drawRoundedRect(_rect2, self.height()//2, self.height()//2)

            _pixmap = QPixmap("checker.png")
            _path = QPainterPath()
            _rect3 = QRectF(_rect.left()+1, _rect.top()+1,
                            _rect.width()-2, _rect.height()-2)
            _path.addRoundedRect(_rect3, self.height()//2, self.height()//2)
            _painter.setClipPath(_path)
            _painter.setClipping(True)
            _painter.drawTiledPixmap(_rect, _pixmap, QPointF(0, 1))
            _painter.setClipping(False)

        # Draw the gradient:
        _gradient = QLinearGradient(_rect.left()+_margin, 0,
                                    _rect.left()+_rect.width()-_margin, 0)
        _gradient_resolution = 100
        _gradient_linspace = np.linspace(0, 1, _gradient_resolution)
        
        if self._type in [ColorSliderType.HUE,
                          ColorSliderType.SATURATION,
                          ColorSliderType.LIGHTNESS]:
            # TODO : implement my own static helper method for HSL <-> RGB
            _qcolor = QColor.fromRgbF(*self._style_color.get_value())
            _hue = _qcolor.hslHueF()
            _sat = _qcolor.hslSaturationF()
            _light = _qcolor.lightnessF()

            if self._type == ColorSliderType.HUE:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromHslF(_i%1, _sat, _light))
            elif self._type == ColorSliderType.SATURATION:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromHslF(_hue, _i, _light))
            elif self._type == ColorSliderType.LIGHTNESS:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromHslF(_hue, _sat, _i))
    
        else:
            _red, _green, _blue, _alpha = tuple(self._style_color.get_value())
            if self._type == ColorSliderType.RED:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromRgbF(_i, _green, _blue))
            elif self._type == ColorSliderType.GREEN:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromRgbF(_red, _i, _blue))
            elif self._type == ColorSliderType.BLUE:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromRgbF(_red, _green, _i))
            elif self._type == ColorSliderType.ALPHA:
                for _i in _gradient_linspace:
                    _gradient.setColorAt(_i, QColor.fromRgbF(_red, _green, _blue, _i))

        _painter.setBrush(QBrush(_gradient))
        _painter.setPen(Qt.NoPen)
        _painter.drawRoundedRect(_rect, self.height()//2, self.height()//2)

        # Draw the handle:
        _ratio = self.value()/self.maximum()
        _handle_x = _rect.left() + _margin + _ratio*(_rect.width() - 2*_margin)
        _painter.setBrush(QBrush(QColor(255, 255, 255, 127)))
        _painter.setPen(QPen(QColor(0, 0, 0, 127), 2))
        _painter.drawEllipse(QPointF(_handle_x, self.height()/2), 4, 4)


class ColorDisplay(QWidget):
    """A color display."""

    _color: np.ndarray

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_color(self, color: Color):
        """Set the displayed color."""
        self._color = color.get_value()
        self.update()
    
    def paintEvent(self, event):
        """Override to paint the color."""
        _painter = QPainter(self)
        _painter.setRenderHint(QPainter.Antialiasing)
        _rect = QRectF(self.rect())
        _rounding = 8

        if self._color[3] < 1:
            _painter.setBrush(QBrush(QColor.fromRgbF(.9, .9, .9)))
            _painter.setPen(Qt.NoPen)
            _painter.drawRoundedRect(_rect, _rounding, _rounding)

            _pixmap = QPixmap("checker.png")
            _path = QPainterPath()
            _rect2 = QRectF(_rect.left()+1, _rect.top()+1,
                            _rect.width()-2, _rect.height()-2)
            _path.addRoundedRect(_rect2, _rounding, _rounding)
            _painter.setClipPath(_path)
            _painter.setClipping(True)
            _painter.drawTiledPixmap(_rect, _pixmap)
            _painter.setClipping(False)

        _painter.setBrush(QBrush(QColor.fromRgbF(*self._color)))
        _painter.setPen(Qt.NoPen)
        _painter.drawRoundedRect(_rect, _rounding, _rounding)


class ColorWheel(QOpenGLWidget):
    """A color wheel and triangle."""

    _initialized: bool
    _circle_program: moderngl.Program
    _circle_array: moderngl.VertexArray
    _triangle_program: moderngl.Program
    _triangle_array: moderngl.VertexArray

    _thickness: float
    _hue: float

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        _width = 160
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFixedWidth(_width)
        self.setFixedHeight(_width)
        self._initialized = False
        self._thickness = .2
        self._hue = 0
    
    def style_from_color(self, color: Color):
        """Style the slider according to a color."""
        # TODO : make my own helper function to convert HSV <-> RGB
        _qcolor = QColor.fromRgbF(*color.get_value())
        self._hue = _qcolor.hsvHueF()
        self.update()
    
    def resizeGL(self, width: int, height: int):
        """React to resizing."""
        _gl_context = moderngl.create_context()
        _gl_context.viewport = (0, 0, width, height)
    
    def initializeGL(self):
        """Setup OpenGL, program and geometry."""
        _gl_context = moderngl.create_context()
        self._init_circle_shader(_gl_context)
        self._init_triangle_shader(_gl_context)
        self._init_arrays(_gl_context)
        self._initialized = True
    
    def _init_circle_shader(self, gl_context: moderngl.Context):
        """Compile shaders and create program."""
        _vertex_code = f"""
        #version 330
		in vec2 in_hz;
        out float hue;
		void main(){{
            float angle = in_hz.x*6.28318530718;
            float z = in_hz.y;

            float out_radius = 1.;
            float in_radius = {1. - self._thickness};

            float rad = mix(out_radius, in_radius, z);
			gl_Position = vec4(vec2(cos(angle), sin(angle))*rad, 0., 1.);
			hue = in_hz.x;
		}}
        """
        _fragment_code = """
        #version 330
		in float hue;
		out vec4 out_color;
		void main(){
            vec3 hsv = vec3(hue, 1., 1.);
            vec4 k = vec4(1., 2./3., 1./3., 3.);
            vec3 p = abs(fract(hsv.xxx + k.xyz)*6. - k.www);
            vec3 rgb = hsv.z*mix(k.xxx, clamp(p-k.xxx, 0., 1.), hsv.y);
			out_color = vec4(rgb, 1.);
		}
        """
        self._circle_program = gl_context.program(
            vertex_shader=_vertex_code,
            fragment_shader=_fragment_code
        )
    
    def _init_triangle_shader(self, gl_context: moderngl.Context):
        """Compile shaders and create program."""
        _vertex_code = f"""
        #version 330
		in vec2 in_sv;
		out vec2 tex_sv;
        uniform float u_hue;
		void main(){{
            float sat = in_sv.x;
            float val = in_sv.y;
            float x = (val - .5)*1.5 - .25;
            float y = val*(sat - .5)*1.732051;
            float radius = {1. - self._thickness};
            float angle = u_hue*6.28318530718;
            angle -= 1.0471975512;
            mat2 transform = mat2(cos(angle), sin(angle),
                                  -sin(angle), cos(angle));
			gl_Position = vec4(transform*vec2(x, y)*radius, 0., 1.);
			tex_sv = in_sv;
		}}
        """
        _fragment_code = """
        #version 330
		in vec2 tex_sv;
		out vec4 out_color;
        uniform float u_hue;
		void main(){
            float sat = tex_sv.x;
            float val = tex_sv.y;
            vec3 hsv = vec3(u_hue, sat, val);
            vec4 k = vec4(1., 2./3., 1./3., 3.);
            vec3 p = abs(fract(hsv.xxx + k.xyz)*6. - k.www);
            vec3 rgb = hsv.z*mix(k.xxx, clamp(p-k.xxx, 0., 1.), hsv.y);
			out_color = vec4(rgb, 1.);
		}
        """
        self._triangle_program = gl_context.program(
            vertex_shader=_vertex_code,
            fragment_shader=_fragment_code
        )
    
    def _init_arrays(self, gl_context: moderngl.Context):
        """Create vertex arrays."""
        # Triangle:
        _points = [0, 0, 0, 1, 1, 1, 1, 0]
        _vertices = np.array(_points, dtype=np.float32)
        _vbo = gl_context.buffer(_vertices.tobytes())
        self._triangle_array = gl_context.vertex_array(
            self._triangle_program, _vbo, "in_sv")

        # Circle:
        _points = []
        for _i in np.linspace(0, 1, 100):
            _points.append(_i)
            _points.append(0)
            _points.append(_i)
            _points.append(1)
        _vertices = np.array(_points, dtype=np.float32)
        _vbo = gl_context.buffer(_vertices.tobytes())
        self._circle_array = gl_context.vertex_array(
            self._circle_program, _vbo, "in_hz")
    
    def paintGL(self):
        """Paint the OpenGL context."""
        if not self._initialized:
            return
        _gl_context = moderngl.create_context()
        _qt_color = self.palette().window().color()
        _gl_context.clear(_qt_color.redF(),
                          _qt_color.greenF(),
                          _qt_color.blueF(), 1)
        self._triangle_program["u_hue"] = self._hue
        self._triangle_array.render(moderngl.TRIANGLE_STRIP)
        self._circle_array.render(moderngl.TRIANGLE_STRIP)


class ColorPicker(QDialog):
    """A color picker dialog."""

    _color: Color
    _color_display: ColorDisplay
    #_color_wheel: ColorWheel
    _rgba_sliders: list[ColorPickerSlider]
    _hsl_sliders: list[ColorPickerSlider]


    def __init__(self, color: Color = None):
        super().__init__()
        self._color = color if color is not None else Color.default()
        self._rgba_sliders = []
        self._hsl_sliders = []

        self.setWindowTitle("Color picker")
        self.setWindowIcon(QIcon(Config.app.icon))
        self.setFixedSize(QSize(400, 272))

        _layout = QVBoxLayout()
        _layout.setContentsMargins(16, 16, 16, 16)
        _layout.setSpacing(6)

        _sliders_layout = QGridLayout()
        _sliders_layout.setContentsMargins(0, 0, 0, 0)
        _sliders_layout.setSpacing(4)
        _sliders_layout.setAlignment(Qt.AlignVCenter)

        _horiz_layout = QHBoxLayout()
        _horiz_layout.setContentsMargins(0, 0, 0, 0)
        _horiz_layout.setSpacing(8)

        _layout.addLayout(_horiz_layout)

        _picker_layout = QVBoxLayout()
        _picker_layout.setContentsMargins(16, 16, 16, 16)
        _picker_layout.setSpacing(16)

        #self._color_wheel = ColorWheel(self)
        self._color_display = ColorDisplay(self)
        
        #_picker_layout.add Widget(self._color_wheel, alignment=Qt.AlignCenter)
        _picker_layout.addWidget(self._color_display)
        
        _horiz_layout.addLayout(_picker_layout)
        _horiz_layout.addLayout(_sliders_layout)

        self.setFocusPolicy(Qt.ClickFocus)

        self._rgba_sliders.append(ColorPickerSlider(self, ColorSliderType.RED))
        self._rgba_sliders.append(ColorPickerSlider(self, ColorSliderType.GREEN))
        self._rgba_sliders.append(ColorPickerSlider(self, ColorSliderType.BLUE))
        self._rgba_sliders.append(ColorPickerSlider(self, ColorSliderType.ALPHA))

        self._hsl_sliders.append(ColorPickerSlider(self, ColorSliderType.HUE))
        self._hsl_sliders.append(ColorPickerSlider(self, ColorSliderType.SATURATION))
        self._hsl_sliders.append(ColorPickerSlider(self, ColorSliderType.LIGHTNESS))

        for _slider in self._rgba_sliders:
            _slider.valueChanged.connect(self._set_color_from_rgba_sliders)
        for _slider in self._hsl_sliders:
            _slider.valueChanged.connect(self._set_color_from_hsl_sliders)

        _sliders_layout.addWidget(self._rgba_sliders[0], 0, 1)
        _sliders_layout.addWidget(self._rgba_sliders[1], 1, 1)
        _sliders_layout.addWidget(self._rgba_sliders[2], 2, 1)
        _sliders_layout.addWidget(QLabel("R", self), 0, 0)
        _sliders_layout.addWidget(QLabel("G", self), 1, 0)
        _sliders_layout.addWidget(QLabel("B", self), 2, 0)

        _sliders_layout.setRowMinimumHeight(3, 16)

        _sliders_layout.addWidget(self._hsl_sliders[0], 4, 1)
        _sliders_layout.addWidget(self._hsl_sliders[1], 5, 1)
        _sliders_layout.addWidget(self._hsl_sliders[2], 6, 1)
        _sliders_layout.addWidget(QLabel("H", self), 4, 0)
        _sliders_layout.addWidget(QLabel("S", self), 5, 0)
        _sliders_layout.addWidget(QLabel("L", self), 6, 0)

        _sliders_layout.setRowMinimumHeight(7, 16)

        _sliders_layout.addWidget(self._rgba_sliders[3], 8, 1)
        _sliders_layout.addWidget(QLabel("A", self), 8, 0)
        
        self._set_rgba_sliders_from_color()
        self._set_hsl_sliders_from_color()
        self._update_displayed_colors()

        DialogService.add_ok_cancel(self, _layout)
        self.setLayout(_layout)

    def _block_signals(self, block: bool = True):
        """Block or unblock all sliders signals."""
        for _slider in self._rgba_sliders:
            _slider.blockSignals(block)
        for _slider in self._hsl_sliders:
            _slider.blockSignals(block)

    def _set_color_from_rgba_sliders(self):
        """React to changes in the RGBA sliders."""
        _red = self._rgba_sliders[0].get_value()
        _green = self._rgba_sliders[1].get_value()
        _blue = self._rgba_sliders[2].get_value()
        _alpha = self._rgba_sliders[3].get_value()
        self._color = Color(_red, _green, _blue, _alpha)

        self._update_displayed_colors()
        self._set_hsl_sliders_from_color()
    
    def _set_color_from_hsl_sliders(self):
        """React to changes in the HSL sliders."""
        _hue = self._hsl_sliders[0].get_value()
        _sat = self._hsl_sliders[1].get_value()
        _light = self._hsl_sliders[2].get_value()
        _alpha = self._rgba_sliders[3].get_value()

        # TODO : implement my own static helper method for HSL <-> RGB
        _qcolor = QColor.fromHslF(_hue, _sat, _light, _alpha)
        _red = _qcolor.redF()
        _green = _qcolor.greenF()
        _blue = _qcolor.blueF()
        self._color = Color(_red, _green, _blue, _alpha)

        self._update_displayed_colors()
        self._set_rgba_sliders_from_color()
    
    def _set_rgba_sliders_from_color(self):
        """Set the RGBA sliders values from the current color."""
        self._block_signals(True)
        _rgba = self._color.get_value()
        for _i in range(4):
            self._rgba_sliders[_i].setValue(
                int(round(self._rgba_sliders[_i].maximum()*_rgba[_i])))
        self._block_signals(False)
    
    def _set_hsl_sliders_from_color(self):
        """Set the HSL sliders values from the current color."""
        self._block_signals(True)
        # TODO : implement my own static helper method for HSL <-> RGB
        _qcolor = QColor.fromRgbF(*self._color.get_value())
        _hsl = [_qcolor.hslHueF(),
                _qcolor.hslSaturationF(),
                _qcolor.lightnessF()]
        for _i in range(3):
            self._hsl_sliders[_i].setValue(
                int(round(self._hsl_sliders[_i].maximum()*_hsl[_i])))
        self._block_signals(False)

    def _update_displayed_colors(self):
        """Change the widgets styles according to the chosen color."""
        self._color_display.set_color(self._color)
        #self._color_wheel.style_from_color(self._color)

        for _slider in self._rgba_sliders:
            _slider.style_from_color(self._color)
        
        for _slider in self._hsl_sliders:
            _slider.style_from_color(self._color)

    def get_color(self) -> Color:
        """Return the selected color."""
        return self._color