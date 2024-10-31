"""
Repository of all modifier templates loaded in the app.

The ModifierRepository class acts as a centralized storage for managing
and accessing all modifier templates that are available within the app.
It ensures that they are loaded once across the application.
"""

from core.entities.modifier_template import ModifierTemplate


class ModifierRepository():
    """Repository of all modifier templates loaded in the app."""

    _repository: dict[str, ModifierTemplate] = dict()
    _structure: dict[str, dict] = dict()

    @classmethod
    def get_repository(cls):
        """Retrieve a reference to the repository dictionary."""
        return cls._repository

    @classmethod
    def get_structure(cls):
        """Retrieve a reference to the modifier browser."""
        return cls._structure

    @classmethod
    def get_template(cls, name_id: str) -> ModifierTemplate:
        """Retrieve a ModifierTemplate based on its name id."""
        if name_id not in cls._repository:
            raise KeyError(f"Modifier '{name_id}' does not "
                           f"exist in the repository.")
        return cls._repository[name_id]
