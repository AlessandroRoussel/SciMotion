"""
Contains all the modifiers loaded in the app.

The ModifierRepository class acts as a centralized storage for managing and
accessing all modifiers that are available within the application. It ensures
that modifiers are loaded once and shared across the application.
"""

from typing import Dict

from utils.singleton import Singleton
from editing.entities.modifier_template import ModifierTemplate


class ModifierRepository(metaclass=Singleton):
    """Repository containing all the modifiers loaded in the application."""

    _repository: Dict[str, ModifierTemplate]  # Dict[unique name: interface]

    def __init__(self):
        # TODO : load configuration if needed
        self._repository = dict()

    def get_repository(self):
        """Retrieve a reference to the repository dictionary."""
        return self._repository
