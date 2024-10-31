"""
ModernGL context.

The GLContext class provides the app
with a centralised moderngl context.
"""

import moderngl


class GLContext():
    """ModernGL context."""

    _context: moderngl.Context = None

    @classmethod
    def get_context(cls) -> moderngl.Context:
        """Return moderngl context."""
        if cls._context is None:
            cls._context = moderngl.create_context(standalone=True)
        return cls._context
