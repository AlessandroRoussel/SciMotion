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
    _src_texture: moderngl.Texture
    _dest_texture: moderngl.Texture

    def __init__(self, _frame: int, _width: int, _height: int):
        self._frame = _frame
        self._width = _width
        self._height = _height
        self._gl_context = None
        self._src_texture = None
        self._dest_texture = None

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

    def get_src_texture(self) -> moderngl.Texture:
        """Return the destination OpenGL texture."""
        if self._src_texture is None:
            self._src_texture = self.get_gl_context().texture(
                (self.get_width(), self.get_height()), 4, dtype="f4")
        return self._src_texture

    def get_dest_texture(self) -> moderngl.Texture:
        """Return the destination OpenGL texture."""
        if self._dest_texture is None:
            self._dest_texture = self.get_gl_context().texture(
                (self.get_width(), self.get_height()), 4, dtype="f4")
        return self._dest_texture

    def roll_textures(self):
        """Replace src texture with dest texture, and clear dest texture."""
        self._src_texture = self.get_dest_texture()
        self._dest_texture = self.get_gl_context().texture(
            (self.get_width(), self.get_height()), 4, dtype="f4")
