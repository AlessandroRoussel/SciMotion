"""
The OpenGL widget within a ViewerPane.

The GLViewer inherits from QOpenGLWidget and provides
an OpenGL context for displaying renders and media.
"""

import numpy as np
from OpenGL import GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QWheelEvent, QMouseEvent, QKeyEvent
from PySide6.QtCore import Qt, QPointF

from utils.config import Config
from utils.image import Image
from gui.services.sequence_gui_service import SequenceGUIService


class GLViewer(QOpenGLWidget):
    """The OpenGL widget within a ViewerPane."""

    _program: int
    _vao: np.uintc
    _texture_id: np.uintc

    _sequence_id: int
    _current_frame: int
    _image: Image
    _zoom: float
    _center_x: float
    _center_y: float
    _fitting_zoom: bool
    _fitting_zoom_max: float
    _mouse_middle_dragging: bool
    _mouse_last_position: QPointF
    _checkerboard: bool
    _texture_loaded: bool

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id
        self._image = None
        self._current_frame = 0
        self._zoom = 1
        self._center_x = .5
        self._center_y = .5
        self._fitting_zoom = False
        self._fitting_zoom_max = None
        self._mouse_middle_dragging = False
        self._mouse_last_position = None
        self._texture_loaded = False
        self._checkerboard = False
        self.update_image()
    
    def set_current_frame(self, frame: int):
        """Set the current frame value."""
        if frame != self._current_frame:
            self._current_frame = frame
            self.update_image()

    def toggle_checkerboard(self, state: bool):
        """Toggle transparency checkerboard status."""
        self._checkerboard = state
        self.update()

    def initializeGL(self):
        """Setup OpenGL, program and geometry."""
        self.init_shaders()
        self.init_quad()
        self.init_texture()
    
    def set_image(self, image: Image):
        """Set the displayed image."""
        self._image = image
        self._texture_loaded = False

    def resizeGL(self, width: int, height: int):
        """React to resizing."""
        GL.glViewport(0, 0, width, height)
        if self._fitting_zoom:
            self.fit_to_frame(self._fitting_zoom_max, False)
    
    def init_shaders(self):
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
        _fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        _vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(_fragment_shader, _fragment_code)
        GL.glShaderSource(_vertex_shader, _vertex_code)
        GL.glCompileShader(_fragment_shader)
        GL.glCompileShader(_vertex_shader)

        self._program = GL.glCreateProgram()
        GL.glAttachShader(self._program, _fragment_shader)
        GL.glAttachShader(self._program, _vertex_shader)
        GL.glLinkProgram(self._program)

        GL.glDeleteShader(_fragment_shader)
        GL.glDeleteShader(_vertex_shader)

    def init_quad(self):
        """Create quad vertex array."""
        _vertices = np.array([0,0,1,0,0,1,1,1], dtype=np.float32)
        
        self._vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao)

        _vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, _vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        _vertices.nbytes,
                        _vertices,
                        GL.GL_STATIC_DRAW)

        # Texture uv attribute
        _uv_attrib = GL.glGetAttribLocation(self._program, "in_uv")
        GL.glEnableVertexAttribArray(_uv_attrib)
        GL.glVertexAttribPointer(_uv_attrib,
                                 2,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 2 * _vertices.itemsize,
                                 GL.ctypes.c_void_p(0))
        GL.glBindVertexArray(0)
        GL.glDeleteBuffers(1, [_vbo])

    def init_texture(self):
        """Initialize the OpenGL texture used to display the image."""
        self._texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def load_texture_from_image(self):
        """Load the image into the OpenGL texture."""
        if self._texture_loaded:
            return
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F,
                        self._image.get_width(),
                        self._image.get_height(),
                        0, GL.GL_RGBA, GL.GL_FLOAT,
                        self._image.get_data_bytes())
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        self._texture_loaded = True

    def paintGL(self):
        """Paint the OpenGL context."""
        _qt_color = self.palette().window().color()
        GL.glClearColor(_qt_color.redF(), _qt_color.greenF(),
                        _qt_color.blueF(), 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        if self._image is not None:
            self.load_texture_from_image()
            GL.glUseProgram(self._program)
            GL.glBindVertexArray(self._vao)

            _transform = self.transformation_matrix()
            _loc = GL.glGetUniformLocation(self._program, "u_transform")
            GL.glUniformMatrix4fv(_loc, 1, GL.GL_TRUE, _transform)

            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
            _tex_loc = GL.glGetUniformLocation(self._program, "u_texture")
            GL.glUniform1i(_tex_loc, 0)

            GL.glUniform1i(
                GL.glGetUniformLocation(self._program, "u_checkerboard"),
                self._checkerboard)
            
            GL.glUniform2f(
                GL.glGetUniformLocation(self._program, "u_dimensions"),
                self.width(),
                self.height())

            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
            GL.glBindVertexArray(0)
            GL.glUseProgram(0)

    def transformation_matrix(self) -> np.ndarray:
        """Return the transformation matrix for displaying the image."""
        _width = self.width()
        _height = self.height()
        _img_width = self._image.get_width()
        _img_height = self._image.get_height()
        _scale_x = self._zoom * _img_width / _width
        _scale_y = self._zoom * _img_height / _height
        _offset_x = self._zoom * (1 - 2*self._center_x) * _img_width/_width
        _offset_y = self._zoom * (-1 + 2*self._center_y) * _img_height/_height
        _transform = np.array([
            [_scale_x, 0, 0, _offset_x],
            [0, _scale_y, 0, _offset_y],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
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
        if self._image is not None:
            _padding = Config.viewer.fit_padding
            _width = self.width() - 2*_padding
            _height = self.height() - 2*_padding
            _img_width = self._image.get_width()
            _img_height = self._image.get_height()
            _zoom = min(_width/_img_width, _height/_img_height)
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

    def widget_to_image_coords(self,
                               widget_x: float,
                               widget_y: float
                               ) -> tuple[float, float]:
        """Convert widget coordinates to image coordinates."""
        _img_width = self._image.get_width()
        _img_height = self._image.get_height()
        _img_x = (widget_x - self.width()/2) / self._zoom
        _img_y = (widget_y - self.height()/2) / self._zoom
        _img_x += self._center_x*_img_width
        _img_y += self._center_y*_img_height
        return _img_x, _img_y
    
    def image_to_widget_coords(self,
                               img_x: float,
                               img_y: float
                               ) -> tuple[float, float]:
        """Convert image coordinates to widget coordinates."""
        _img_width = self._image.get_width()
        _img_height = self._image.get_height()
        _widget_x = (img_x - self._center_x*_img_width) * self._zoom
        _widget_y = (img_y - self._center_y*_img_height) * self._zoom
        _widget_x += self.width()/2
        _widget_y += self.height()/2
        return _widget_x, _widget_y
    
    def wheel_scroll(self, event: QWheelEvent):
        """Handle the wheel scroll event."""
        if self._image is None:
            return
        _delta = event.angleDelta().y()
        _mouse_pos = event.position()
        _img_x, _img_y = self.widget_to_image_coords(_mouse_pos.x(),
                                                        _mouse_pos.y())
        _img_width = self._image.get_width()
        _img_height = self._image.get_height()
        _factor = np.exp(_delta / 100. * Config.viewer.zoom_sensitivity)
        self.set_zoom(self._zoom * _factor)
        if Config.viewer.zoom_around_cursor:
            self._center_x = _img_x/_img_width - (
                _img_x/_img_width - self._center_x)/_factor
            self._center_y = _img_y/_img_height - (
                _img_y/_img_height - self._center_y)/_factor
        self._fitting_zoom = False
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle the mouse press event."""
        if self._image is not None and event.button() == Qt.MiddleButton:
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
        if self._image is not None and self._mouse_middle_dragging:
            _current_pos = event.position()
            _delta = _current_pos - self._mouse_last_position
            self.middle_mouse_button_drag(_delta)
            self._mouse_last_position = _current_pos

    def middle_mouse_button_drag(self, delta: float):
        """Drag using middle mouse button."""
        if self._image is None:
            return
        _img_width = self._image.get_width()
        _img_height = self._image.get_height()
        self._center_x -= delta.x() / self._zoom / _img_width
        self._center_y -= delta.y() / self._zoom / _img_height
        self.update()

    def update_image(self):
        """Update the displayed image."""
        self.set_image(
            SequenceGUIService.request_image_from_sequence(
                self._sequence_id, self._current_frame))
        self.update()
