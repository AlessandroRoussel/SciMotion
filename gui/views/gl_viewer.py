"""
The OpenGL widget within a ViewerPane.

The GLViewer inherits from QOpenGLWidget and provides
an OpenGL context for displaying renders and media.
"""

from pathlib import Path
import numpy as np
from OpenGL import GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from utils.config import Config
from utils.image import Image
from core.entities.sequence import Sequence
from core.entities.solid_layer import SolidLayer
from core.services.render_service import RenderService
from core.services.layer_service import LayerService
from core.services.modifier_service import ModifierService
from data_types.color import Color


class GLViewer(QOpenGLWidget):
    """The OpenGL widget within a ViewerPane."""

    _program: int
    _vao: np.uintc
    _texture_id: np.uintc

    _image: Image
    _zoom: float
    _center_x: float
    _center_y: float
    _checkerboard: bool

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._zoom = 1
        self._center_x = .5
        self._center_y = .5
        self._image = None
        self._checkerboard = True
    
    def initializeGL(self):
        """Setup OpenGL, program and geometry."""
        _qt_color = self.palette().color(self.backgroundRole())
        GL.glClearColor(_qt_color.redF(),
                        _qt_color.greenF(),
                        _qt_color.blueF(),
                        1)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self.init_shaders()
        self.init_quad()
        self.init_texture()


        ##############
        # TEST       #
        ##############

        ModifierService().load_modifiers_from_directory(Path("modifiers"))
        _sequence = Sequence("", 960, 540, 0, 0)
        _layer = SolidLayer("", 0, 0, 960, 540, Color.BLACK)
        _modifier = ModifierService().modifier_from_template("linear_gradient")
        ModifierService().add_modifier_to_layer(_modifier, _layer)
        LayerService().add_layer_to_sequence(_layer, _sequence)
        self._image = RenderService().render_sequence_frame(_sequence)


    
    def resizeGL(self, width: int, height: int):
        """React to resizing."""
        GL.glViewport(0, 0, width, height)
    
    def init_shaders(self):
        """Compile shaders and create program."""
        _vertex_code = """
        #version 330
		in vec2 in_pos;
		in vec2 in_uv;
		out vec2 tex_uv;
		uniform mat4 u_transform;
		void main(){
			gl_Position = u_transform * vec4(in_pos,0.,1.);
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
                Config().viewer.checkerboard_size)+""";
			vec2 q = xy/size-2.*floor(xy/2./size);
			return mix("""+"{0:.2f}".format(
                Config().viewer.checkerboard_color_a)+""",
			  """+"{0:.2f}".format(
                  Config().viewer.checkerboard_color_b)+""",
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
        _vertices = np.array([
            -1, -1, 0, 0,
            1, -1, 1, 0,
            -1, 1, 0, 1,
            1, 1, 1, 1], dtype=np.float32)
        
        self._vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao)

        _vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, _vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        _vertices.nbytes,
                        _vertices,
                        GL.GL_STATIC_DRAW)

        # Position attribute
        _pos_attrib = GL.glGetAttribLocation(self._program, "in_pos")
        GL.glEnableVertexAttribArray(_pos_attrib)
        GL.glVertexAttribPointer(_pos_attrib,
                                 2,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 4 * _vertices.itemsize,
                                 GL.ctypes.c_void_p(0))

        # Texture uv attribute
        _uv_attrib = GL.glGetAttribLocation(self._program, "in_uv")
        GL.glEnableVertexAttribArray(_uv_attrib)
        GL.glVertexAttribPointer(_uv_attrib,
                                 2,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 4 * _vertices.itemsize,
                                 GL.ctypes.c_void_p(2 * _vertices.itemsize))
        GL.glBindVertexArray(0)

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
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F,
                        self._image.get_width(),
                        self._image.get_height(),
                        0, GL.GL_RGBA, GL.GL_FLOAT,
                        self._image.get_data_bytes())
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def paintGL(self):
        """Paint the OpenGL context."""
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if self._image is not None:
            # TODO : not load texture every time, but only when changing image
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
        