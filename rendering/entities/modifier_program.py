"""
Represents an effect that the user can apply to a Layer.

The Modifier class contains the GLSL code
for a compute shader that can be compiled into
an OpenGL program.
"""

from typing import Dict

from OpenGL import GL


class Modifier:
    """Represents an OpenGL compute shader."""

    _code: str
    _compiled: bool
    _program: GL.GLuint
    _uniform_locations: Dict[str, GL.GLint]

    def __init__(self, glsl_code: str):
        self._code = glsl_code
        self._compiled = False
        self._program = None
        self._uniform_locations = dict()

    def __del__(self):
        """Clear OpenGL objects."""
        if self._compiled:
            GL.glDeleteProgram(self._program)

    def _compile_program(self):
        """Compile code to OpenGL program."""
        if not self._compiled:
            _shader = GL.glCreateShader(GL.GL_COMPUTE_SHADER)
            GL.glShaderSource(_shader, self._code)
            GL.glCompileShader(_shader)

            self._program = GL.glCreateProgram()
            GL.glAttachShader(self._program, _shader)
            GL.glLinkProgram(self._program)

            GL.glDeleteShader(_shader)
            self.compiled = True

    def get_program(self) -> GL.GLuint:
        """Retrieve the OpenGL program."""
        if not self._compiled:
            self._compile_program()
        return self._program

    def get_uniform_location(self, uniform_name: str) -> GL.GLint:
        """Retrieve the location of a uniform."""
        if not self._compiled:
            self._compile_program()
        if uniform_name not in self._uniform_locations:
            _location = GL.glGetUniformLocation(self._program, uniform_name)
            self._uniform_locations[uniform_name] = _location
        return self._uniform_locations[uniform_name]
