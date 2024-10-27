"""
Repository of all modifier templates loaded in the app.

The ModifierRepository singleton class acts as a centralized storage for
managing and accessing all modifier templates that are available within the
application. It ensures that they are loaded once across the application.
"""

from utils.singleton import Singleton
from editing.entities.modifier_template import ModifierTemplate


class ModifierRepository(metaclass=Singleton):
    """Repository of all modifier templates loaded in the app."""

    _repository: dict[str, ModifierTemplate]  # dict[name id: template]

    def __init__(self):
        # TODO : load configuration if needed
        self._repository = dict()

    def get_repository(self):
        """Retrieve a reference to the repository dictionary."""
        return self._repository
