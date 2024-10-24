"""
A singleton metaclass.

A singleton class ensures that only one
instance of the class can ever exist.
"""


class Singleton(type):
    """A singleton metaclass."""

    _instances = dict()

    def __call__(cls, *args, **kwargs):
        """Create instance if needed only."""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
        return instance
