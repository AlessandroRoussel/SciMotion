"""
Provides useful information about the rendering context.

A RenderContext is used to provide a ModifierProgram with various
information about the rendering context, such as the Layer dimensions,
as well as the source and destination textures, and a ModernGL context
for running shaders if needed...
"""

import moderngl

from core.entities.gl_context import GLContext
from core.entities.sequence_context import SequenceContext


class RenderContext:
    """Provides useful information about the rendering context."""

    _width: int
    _height: int
    _src_texture: moderngl.Texture
    _dest_texture: moderngl.Texture
    _sequence_context: SequenceContext

    def __init__(self,
                 width: int,
                 height: int,
                 sequence_context: SequenceContext):
        self._width = width
        self._height = height
        self._sequence_context = sequence_context
        self._src_texture = None
        self._dest_texture = None

    def get_sequence_context(self) -> SequenceContext:
        """Return the sequence context."""
        return self._sequence_context

    def release_dest_texture(self):
        """Release the destination moderngl texture."""
        if self._dest_texture is not None:
            self._dest_texture.release()

    def get_gl_context(self) -> moderngl.Context:
        """Return the moderngl context."""
        return GLContext.get_context()

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
