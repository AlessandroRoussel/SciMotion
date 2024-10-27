"""
Provides useful information about the rendering context.

A RenderContext is used to provide a ModifierProgram with various
information about the rendering context, such as the Layer dimensions,
the current frame number, and so on, as well as the source and destination
textures, and a ModernGL context for running shaders if needed...
"""

import moderngl


class RenderContext:
    """Provides useful information about the rendering context."""

    _frame: int
    _width: int
    _height: int
    _gl_context: moderngl.Context
    _result_texture: moderngl.Texture

    def __init__(self, _frame: int, _width: int, _height: int):
        self._frame = _frame
        self._width = _width
        self._height = _height
        self._gl_context = None
        self._result_texture = None

    def get_gl_context(self) -> moderngl.Context:
        """Return a moderngl standalone context."""
        if self._gl_context is None:
            self._gl_context = moderngl.create_context(standalone=True)
        return self._gl_context

    def get_width(self) -> int:
        """Return the width of the Layer."""
        return self._width

    def get_height(self) -> int:
        """Return the height of the Layer."""
        return self._height

    def set_result_texture(self, result_texture: moderngl.Texture):
        """Set the resulting texture."""
        self._result_texture = result_texture
