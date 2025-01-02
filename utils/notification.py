"""A basic callback class for connecting signals to functions."""

from typing import Callable, Any


class Notification:
    """A basic callback class for connecting signals to functions."""

    _blocked: bool
    _callbacks: list[Callable]

    def __init__(self):
        self._callbacks = []
        self._blocked = False

    def connect(self, callback: Callable):
        """Connect this notification to a callback function."""
        self._callbacks.append(callback)
    
    def block(self, blocked: bool = True):
        """Block / unblock signal."""
        self._blocked = blocked

    def emit(self, *values: Any):
        """Emit the notification and execute callbacks."""
        if self._blocked:
            return
        for _callback in self._callbacks:
            _callback(*values)
