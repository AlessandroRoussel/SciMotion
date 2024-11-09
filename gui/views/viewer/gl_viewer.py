"""
The OpenGL widget within a ViewerPane.

The GLViewer inherits from QOpenGLWidget and provides
an OpenGL context for displaying renders and media.
"""

import time

import numpy as np
import moderngl
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QWheelEvent, QMouseEvent, QKeyEvent
from PySide6.QtCore import Qt, QPointF

from utils.config import Config
from utils.image import Image
from gui.services.sequence_gui_service import SequenceGUIService


class GLViewer(QOpenGLWidget):
    """The OpenGL widget within a ViewerPane."""
    _program: moderngl.Program
    _vao: moderngl.VertexArray
    _texture: moderngl.Texture

    _sequence_id: int
    _current_frame: int
    _zoom: float
    _center_x: float
    _center_y: float
    _fitting_zoom: bool
    _fitting_zoom_max: float
    _mouse_middle_dragging: bool
    _mouse_last_position: QPointF
    _checkerboard: bool

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id
        self._current_frame = 0
        self._zoom = 1
        self._center_x = .5
        self._center_y = .5
        self._fitting_zoom = False
        self._fitting_zoom_max = None
        self._mouse_middle_dragging = False
        self._mouse_last_position = None
        self._checkerboard = False
        self._texture = None
        self.setFocusPolicy(Qt.WheelFocus)
        self.update_texture()
    
    def set_current_frame(self, frame: int):
        """Set the current frame value."""
        if frame != self._current_frame:
            self._current_frame = frame
            self.update_texture()

    def toggle_checkerboard(self, state: bool):
        """Toggle transparency checkerboard status."""
        self._checkerboard = state
        self.update()
    
    def set_texture(self, texture: moderngl.Texture):
        """Set the displayed texture."""
        if self._texture is not None:
            self._texture.release()
        self._texture = texture
        self._texture.repeat_x = False
        self._texture.repeat_y = False
        self._texture.filter = moderngl.LINEAR, moderngl.NEAREST

    def resizeGL(self, width: int, height: int):
        """React to resizing."""
        _gl_context = moderngl.create_context()
        _gl_context.viewport = (0, 0, width, height)
        if self._fitting_zoom:
            self.fit_to_frame(self._fitting_zoom_max, False)

    def initializeGL(self):
        """Setup OpenGL, program and geometry."""
        _gl_context = moderngl.create_context()
        self.init_shaders(_gl_context)
        self.init_quad(_gl_context)

    def init_shaders(self, gl_context: moderngl.Context):
        """Compile shaders and create program."""
        _vertex_code = """
        #version 330
		in vec2 in_uv;
		out vec2 tex_uv;
		uniform mat4 u_transform;
		void main(){
			gl_Position = u_transform * vec4(in_uv*2.-1.,0.,1.);
			tex_uv = in_uv;
		}
        """
        _fragment_code = """
        #version 330
		in vec2 tex_uv;
		out vec4 out_color;
		uniform sampler2D u_texture;
		uniform bool u_checkerboard;
		uniform vec2 u_dimensions;

		float checkerTexture(vec2 xy){
			float size = """+"{0:.2f}".format(
                Config.viewer.checkerboard_size)+""";
			vec2 q = xy/size-2.*floor(xy/2./size);
			return mix("""+"{0:.2f}".format(
                Config.viewer.checkerboard_color_a)+""",
			  """+"{0:.2f}".format(
                  Config.viewer.checkerboard_color_b)+""",
			  float(q.x < 1. ^^ q.y < 1.));
		}
		
		void main(){
			vec4 color = texture(u_texture, tex_uv);
			vec3 back_color = vec3(0.);
			if(u_checkerboard){
				vec2 checkerboard_coord = gl_FragCoord.xy - u_dimensions*.5;
				back_color = vec3(checkerTexture(checkerboard_coord));
			}
			vec3 blended_color = mix(back_color, color.rgb, color.a);
			out_color = vec4(blended_color, 1.);
		}
        """
        self._program = gl_context.program(
            vertex_shader=_vertex_code,
            fragment_shader=_fragment_code
        )
    
    def init_quad(self, gl_context: moderngl.Context):
        """Create quad vertex array."""
        _vertices = np.array([0,0,1,0,0,1,1,1], dtype=np.float32)
        _vbo = gl_context.buffer(_vertices.tobytes())
        self._vao = gl_context.vertex_array(self._program, _vbo, "in_uv")

    def paintGL(self):
        """Paint the OpenGL context."""
        _gl_context = moderngl.create_context()
        _qt_color = self.palette().window().color()
        _gl_context.clear(_qt_color.redF(), _qt_color.greenF(),
                                        _qt_color.blueF(), 1)
        if self._texture is not None:
            self._texture.use(location=0)
            self._program["u_texture"] = 0
            _transform = self.transformation_matrix()
            self._program["u_transform"] = _transform
            self._program["u_checkerboard"] = self._checkerboard
            self._program["u_dimensions"] = self.width(), self.height()
            self._vao.render(moderngl.TRIANGLE_STRIP)

    def transformation_matrix(self) -> np.ndarray:
        """Return the transformation matrix for displaying the texture."""
        _width = self.width()
        _height = self.height()
        _tex_width = self._texture.width
        _tex_height = self._texture.height
        _scale_x = self._zoom * _tex_width / _width
        _scale_y = self._zoom * _tex_height / _height
        _offset_x = self._zoom * (1 - 2*self._center_x) * _tex_width/_width
        _offset_y = self._zoom * (-1 + 2*self._center_y) * _tex_height/_height
        _transform = np.array([
            _scale_x, 0, 0, 0,
            0, _scale_y, 0, 0,
            0, 0, 1, 0,
            _offset_x, _offset_y, 0, 1
        ], dtype=np.float32)
        return _transform

    def set_zoom(self, value: float):
        self._zoom = max(Config.viewer.min_zoom,
                         min(value, Config.viewer.max_zoom))

    def get_zoom(self) -> float:
        """Return the zoom value."""
        return self._zoom

    def fit_to_frame(self,
                     max_zoom: float = None,
                     update: bool = True,
                     just_once: bool = False):
        """Set the viewer to fit its contents."""
        self._center_x = .5
        self._center_y = .5
        if self._texture is not None:
            _padding = Config.viewer.fit_padding
            _width = self.width() - 2*_padding
            _height = self.height() - 2*_padding
            _tex_width = self._texture.width
            _tex_height = self._texture.height
            _zoom = min(_width/_tex_width, _height/_tex_height)
            if max_zoom is not None:
                _zoom = min(_zoom, max_zoom)
            self.set_zoom(_zoom)
        self._fitting_zoom = not just_once
        self._fitting_zoom_max = max_zoom
        if update:
            self.update()
	
    def choose_zoom(self, zoom: float):
        """Choose a specific zoom value."""
        self.set_zoom(zoom)
        self._fitting_zoom = False
        self.update()

    def widget_to_texture_coords(self,
                                 widget_x: float,
                                 widget_y: float
                                 ) -> tuple[float, float]:
        """Convert widget coordinates to texture coordinates."""
        _tex_width = self._texture.width
        _tex_height = self._texture.height
        _img_x = (widget_x - self.width()/2) / self._zoom
        _img_y = (widget_y - self.height()/2) / self._zoom
        _img_x += self._center_x*_tex_width
        _img_y += self._center_y*_tex_height
        return _img_x, _img_y
    
    def texture_to_widget_coords(self,
                                 img_x: float,
                                 img_y: float
                                 ) -> tuple[float, float]:
        """Convert texture coordinates to widget coordinates."""
        _tex_width = self._texture.width
        _tex_height = self._texture.height
        _widget_x = (img_x - self._center_x*_tex_width) * self._zoom
        _widget_y = (img_y - self._center_y*_tex_height) * self._zoom
        _widget_x += self.width()/2
        _widget_y += self.height()/2
        return _widget_x, _widget_y
    
    def wheel_scroll(self, event: QWheelEvent):
        """Handle the wheel scroll event."""
        if self._texture is None:
            return
        _delta = event.angleDelta().y()
        _mouse_pos = event.position()
        _img_x, _img_y = self.widget_to_texture_coords(_mouse_pos.x(),
                                                       _mouse_pos.y())
        _tex_width = self._texture.width
        _tex_height = self._texture.height
        _factor = np.exp(_delta / 100. * Config.viewer.zoom_sensitivity)
        self.set_zoom(self._zoom * _factor)
        if Config.viewer.zoom_around_cursor:
            self._center_x = _img_x/_tex_width - (
                _img_x/_tex_width - self._center_x)/_factor
            self._center_y = _img_y/_tex_height - (
                _img_y/_tex_height - self._center_y)/_factor
        self._fitting_zoom = False
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if self._texture is not None and event.button() == Qt.MiddleButton:
            self._mouse_middle_dragging = True
            self._mouse_last_position = event.position()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle the mouse release event."""
        if event.button() == Qt.MiddleButton:
            self._mouse_middle_dragging = False
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle the mouse move event."""
        if self._texture is not None and self._mouse_middle_dragging:
            _current_pos = event.position()
            _delta = _current_pos - self._mouse_last_position
            self.middle_mouse_button_drag(_delta)
            self._mouse_last_position = _current_pos

    def middle_mouse_button_drag(self, delta: float):
        """Drag using middle mouse button."""
        if self._texture is None:
            return
        _tex_width = self._texture.width
        _tex_height = self._texture.height
        self._center_x -= delta.x() / self._zoom / _tex_width
        self._center_y -= delta.y() / self._zoom / _tex_height
        self.update()

    def update_texture(self):
        """Update the displayed texture."""
        self.set_texture(
            SequenceGUIService.request_texture_from_sequence(
                self._sequence_id, self._current_frame))
        self.update()
