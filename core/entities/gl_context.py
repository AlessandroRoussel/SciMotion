"""
ModernGL context singleton.

The GLContext singleton class provides the
app with a centralised moderngl context.
"""

import moderngl

from utils.singleton import Singleton


class GLContext(metaclass=Singleton):
    """ModernGL context singleton."""

    _context: moderngl.Context

    def __init__(self):
        # TODO : load configuration if needed
        self._context = None

    def get_context(self) -> moderngl.Context:
        """Return moderngl context."""
        if self._context is None:
            self._context = moderngl.create_context(standalone=True)
        return self._context
