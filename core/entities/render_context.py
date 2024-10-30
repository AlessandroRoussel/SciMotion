"""
Provides useful information about the rendering context.

A RenderContext is used to provide a ModifierProgram with various
information about the rendering context, such as the Layer dimensions,
the current frame number, and so on, as well as the source and destination
textures, and a ModernGL context for running shaders if needed...
"""

import moderngl

from utils.gl_context import GLContext


class RenderContext:
    """Provides useful information about the rendering context."""

    _width: int
    _height: int
    _src_texture: moderngl.Texture
    _dest_texture: moderngl.Texture

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._src_texture = None
        self._dest_texture = None

    def get_gl_context(self) -> moderngl.Context:
        """Return the moderngl context."""
        return GLContext().get_context()

    def get_width(self) -> int:
        """Return the width of the Layer."""
        return self._width

    def get_height(self) -> int:
        """Return the height of the Layer."""
        return self._height

    def get_src_texture(self) -> moderngl.Texture:
        """Return the destination moderngl texture."""
        if self._src_texture is None:
            self._src_texture = self.get_gl_context().texture(
                (self.get_width(), self.get_height()), 4, dtype="f4")
        return self._src_texture

    def get_dest_texture(self) -> moderngl.Texture:
        """Return the destination moderngl texture."""
        if self._dest_texture is None:
            self._dest_texture = self.get_gl_context().texture(
                (self.get_width(), self.get_height()), 4, dtype="f4")
        return self._dest_texture

    def roll_textures(self):
        """Replace src texture with dest texture, and clear dest texture."""
        self._src_texture = self.get_dest_texture()
        self._dest_texture = self.get_gl_context().texture(
            (self.get_width(), self.get_height()), 4, dtype="f4")

    def set_src_texture(self, texture: moderngl.Texture):
        """Set the source moderngl texture."""
        self._src_texture = texture
