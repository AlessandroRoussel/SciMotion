"""
Provides useful information about the rendering context.

A RenderContext is used to provide a ModifierProgram with various
information about the rendering context, such as the Layer dimensions,
the current frame number, and so on, as well as the source and destination
textures, and a ModernGL context for running shaders if needed...
"""

from moderngl import Context, Texture


class RenderContext:
    """Provides useful information about the rendering context."""

    _width: int
    _height: int
    _gl_context: Context
    _src_texture: Texture

    def __init__(self):
        pass
