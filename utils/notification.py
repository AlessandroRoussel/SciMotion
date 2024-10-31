"""A basic callback class for connecting signals to functions."""

from typing import Callable, Any


class Notification:
    """A basic callback class for connecting signals to functions."""

    _callbacks: list[Callable]

    def __init__(self):
        self._callbacks = []

    def connect(self, callback: Callable):
        """Connect this notification to a callback function."""
        self._callbacks.append(callback)
    
    def emit(self, *values: Any):
        """Emit the notification and execute callbacks."""
        for _callback in self._callbacks:
            _callback(*values)
