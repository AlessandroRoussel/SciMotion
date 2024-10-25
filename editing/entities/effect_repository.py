"""
Contains all the effects loaded in the app.

The EffectRepository class acts as a centralized storage for managing and
accessing all effects that are available within the application. It ensures
that effects are loaded once and shared across the application.
"""

from typing import Dict

from utils.singleton import Singleton
from editing.entities.effect import Effect


class EffectRepository(metaclass=Singleton):
    """Repository containing all the effects loaded in the application."""

    _repository: Dict[int: Effect]

    def __init__(self):
        # TODO : load configuration if needed
        self._repository = dict()
