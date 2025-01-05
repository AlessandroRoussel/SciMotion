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
from utils.color_management import ColorSpace
from gui.views.inputs.type_number_input import TypeNumberInput


class ColorSliderType(Enum):
    """Enumerate all the color slider types."""

    RED = 0
    GREEN = 1
    BLUE = 2
    ALPHA = 3
    HUE = 4
    CHROMA = 5
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
                          ColorSliderType.CHROMA,
                          ColorSliderType.LIGHTNESS]:
            _lch = self._style_color.get_value(ColorSpace.OKLCH)
            for _i in _gradient_linspace:
                if self._type == ColorSliderType.HUE:
                    _color = Color(_lch[0], _lch[1], _i%1,
                                    color_space=ColorSpace.OKLCH)
                elif self._type == ColorSliderType.CHROMA:
                    _color = Color(_lch[0], _i, _lch[2],
                                   color_space=ColorSpace.OKLCH)
                elif self._type == ColorSliderType.LIGHTNESS:
                    _color = Color(_i, _lch[1], _lch[2],
                                   color_space=ColorSpace.OKLCH)
                
                _rgba = _color.get_value(ColorSpace.SRGB)
                if np.max(_rgba[:3]) <= 1 and np.min(_rgba[:3]) >= 0:
                   _qcolor = QColor.fromRgbF(*_rgba[:3])
                else:
                    _qcolor = QColor.fromRgbF(0, 0, 0, 0)
                _gradient.setColorAt(_i, _qcolor)
    
        else:
            _rgb = self._style_color.get_value(ColorSpace.SRGB)
            if self._type == ColorSliderType.RED:
                for _i in _gradient_linspace:
                    _qcolor = QColor.fromRgbF(_i, _rgb[1], _rgb[2])
                    _gradient.setColorAt(_i, _qcolor)
            elif self._type == ColorSliderType.GREEN:
                for _i in _gradient_linspace:
                    _qcolor = QColor.fromRgbF(_rgb[0], _i, _rgb[2])
                    _gradient.setColorAt(_i, _qcolor)
            elif self._type == ColorSliderType.BLUE:
                for _i in _gradient_linspace:
                    _qcolor = QColor.fromRgbF(_rgb[0], _rgb[1], _i)
                    _gradient.setColorAt(_i, _qcolor)
            elif self._type == ColorSliderType.ALPHA:
                for _i in _gradient_linspace:
                    _qcolor = QColor.fromRgbF(_rgb[0], _rgb[1], _rgb[2], _i)
                    _gradient.setColorAt(_i, _qcolor)

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
        self._color = color.get_value(ColorSpace.SRGB)
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
        _painter.setPen(QPen(self.palette().window().color(), 1))
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
        self._hue = color.get_value(ColorSpace.HSV)[0]
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
    _rgba_inputs: list[TypeNumberInput]
    _lch_sliders: list[ColorPickerSlider]


    def __init__(self, color: Color = None):
        super().__init__()
        self._color = color if color is not None else Color.default()
        self._rgba_sliders = []
        self._lch_sliders = []

        self.setWindowTitle("Color picker")
        self.setWindowIcon(QIcon(Config.app.icon))
        self.setFixedSize(QSize(400, 272))

        _layout = QVBoxLayout()
        _layout.setContentsMargins(16, 16, 16, 16)
        _layout.setSpacing(6)

        _sliders_layout = QGridLayout()
        _sliders_layout.setContentsMargins(0, 16, 0, 16)
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

        self._lch_sliders.append(ColorPickerSlider(self, ColorSliderType.LIGHTNESS))
        self._lch_sliders.append(ColorPickerSlider(self, ColorSliderType.CHROMA))
        self._lch_sliders.append(ColorPickerSlider(self, ColorSliderType.HUE))

        self._rgba_inputs = [TypeNumberInput(self, min=0, max=1, decimals=2)
                             for _i in range(4)]
        self._lch_inputs = [TypeNumberInput(self, min=0, max=1, decimals=2)
                             for _i in range(3)]

        for _slider in self._rgba_sliders:
            _slider.valueChanged.connect(self._set_color_from_rgba_sliders)
        for _slider in self._lch_sliders:
            _slider.valueChanged.connect(self._set_color_from_lch_sliders)
        for _input in self._rgba_inputs:
            _input.value_changed.connect(self._set_color_from_rgba_inputs)
        for _input in self._lch_inputs:
            _input.value_changed.connect(self._set_color_from_lch_inputs)

        _sliders_layout.addWidget(QLabel("r", self), 0, 0)
        _sliders_layout.addWidget(QLabel("g", self), 1, 0)
        _sliders_layout.addWidget(QLabel("b", self), 2, 0)
        _sliders_layout.addWidget(self._rgba_sliders[0], 0, 1)
        _sliders_layout.addWidget(self._rgba_sliders[1], 1, 1)
        _sliders_layout.addWidget(self._rgba_sliders[2], 2, 1)
        _sliders_layout.addWidget(self._rgba_inputs[0], 0, 2)
        _sliders_layout.addWidget(self._rgba_inputs[1], 1, 2)
        _sliders_layout.addWidget(self._rgba_inputs[2], 2, 2)

        _sliders_layout.setRowMinimumHeight(3, 16)

        _sliders_layout.addWidget(QLabel("h", self), 4, 0)
        _sliders_layout.addWidget(QLabel("c", self), 5, 0)
        _sliders_layout.addWidget(QLabel("l", self), 6, 0)
        _sliders_layout.addWidget(self._lch_sliders[2], 4, 1)
        _sliders_layout.addWidget(self._lch_sliders[1], 5, 1)
        _sliders_layout.addWidget(self._lch_sliders[0], 6, 1)
        _sliders_layout.addWidget(self._lch_inputs[2], 4, 2)
        _sliders_layout.addWidget(self._lch_inputs[1], 5, 2)
        _sliders_layout.addWidget(self._lch_inputs[0], 6, 2)

        _sliders_layout.setRowMinimumHeight(7, 16)

        _sliders_layout.addWidget(QLabel("a", self), 8, 0)
        _sliders_layout.addWidget(self._rgba_sliders[3], 8, 1)
        _sliders_layout.addWidget(self._rgba_inputs[3], 8, 2)
        
        self._set_rgba_sliders_from_color()
        self._set_lch_sliders_from_color()
        self._set_rgba_inputs_from_color()
        self._set_lch_inputs_from_color()
        self._update_displayed_colors()

        DialogService.add_ok_cancel(self, _layout)
        self.setLayout(_layout)

    def _block_signals(self, block: bool = True):
        """Block or unblock all sliders signals."""
        for _slider in self._rgba_sliders:
            _slider.blockSignals(block)
        for _slider in self._lch_sliders:
            _slider.blockSignals(block)
        for _input in self._rgba_inputs:
            _input.block_signals(block)
        for _input in self._lch_inputs:
            _input.block_signals(block)

    def _set_color_from_rgba_sliders(self):
        """React to changes in the RGBA sliders."""
        _rgba = [_slider.get_value() for _slider in self._rgba_sliders]
        self._color = Color(*_rgba, color_space=ColorSpace.SRGB)

        self._update_displayed_colors()
        self._set_lch_sliders_from_color()
        self._set_rgba_inputs_from_color()
        self._set_lch_inputs_from_color()
    
    def _set_color_from_lch_sliders(self):
        """React to changes in the LCH sliders."""
        _lch = [_slider.get_value() for _slider in self._lch_sliders]
        _alpha = self._rgba_sliders[3].get_value()
        self._color = Color(*_lch, _alpha, color_space=ColorSpace.OKLCH)

        self._update_displayed_colors()
        self._set_rgba_sliders_from_color()
        self._set_rgba_inputs_from_color()
        self._set_lch_inputs_from_color()
    
    def _set_color_from_rgba_inputs(self, value):
        """React to changes in the RGBA inputs."""
        _rgba = [_input.get_value().get_value() for _input in self._rgba_inputs]
        self._color = Color(*_rgba, color_space=ColorSpace.SRGB)

        self._update_displayed_colors()
        self._set_rgba_sliders_from_color()
        self._set_lch_sliders_from_color()
        self._set_lch_inputs_from_color()
    
    def _set_color_from_lch_inputs(self, value):
        """React to changes in the LCH inputs."""
        _lch = [_input.get_value().get_value() for _input in self._lch_inputs]
        _alpha = self._rgba_inputs[3].get_value().get_value()
        self._color = Color(*_lch, _alpha, color_space=ColorSpace.OKLCH)

        self._update_displayed_colors()
        self._set_rgba_sliders_from_color()
        self._set_lch_sliders_from_color()
        self._set_rgba_inputs_from_color()
    
    def _set_rgba_sliders_from_color(self):
        """Set the RGBA sliders values from the current color."""
        self._block_signals(True)
        _rgba = self._color.get_value(ColorSpace.SRGB)
        for _i in range(4):
            self._rgba_sliders[_i].setValue(
                int(round(self._rgba_sliders[_i].maximum()*_rgba[_i])))
        self._block_signals(False)
    
    def _set_lch_sliders_from_color(self):
        """Set the LCH sliders values from the current color."""
        self._block_signals(True)
        _lch = self._color.get_value(ColorSpace.OKLCH)
        for _i in range(3):
            self._lch_sliders[_i].setValue(
                int(round(self._lch_sliders[_i].maximum()*_lch[_i])))
        self._block_signals(False)
    
    def _set_rgba_inputs_from_color(self):
        """Set the RGBA inputs values from the current color."""
        self._block_signals(True)
        _rgba = self._color.get_value(ColorSpace.SRGB)
        for _i in range(4):
            self._rgba_inputs[_i].set_value(_rgba[_i])
        self._block_signals(False)
    
    def _set_lch_inputs_from_color(self):
        """Set the LCH inputs values from the current color."""
        self._block_signals(True)
        _lch = self._color.get_value(ColorSpace.OKLCH)
        for _i in range(3):
            self._lch_inputs[_i].set_value(_lch[_i])
        self._block_signals(False)

    def _update_displayed_colors(self):
        """Change the widgets styles according to the chosen color."""
        self._color_display.set_color(self._color)
        #self._color_wheel.style_from_color(self._color)

        for _slider in self._rgba_sliders:
            _slider.style_from_color(self._color)
        
        for _slider in self._lch_sliders:
            _slider.style_from_color(self._color)

    def get_color(self) -> Color:
        """Return the selected color."""
        return self._color