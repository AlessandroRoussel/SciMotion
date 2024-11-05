"""
Service concerning the project in general.

The ProjectService class defines services within the core
package, concerning the project. This includes adding new
sequences to the project, changing parameters...
"""

from core.entities.project import Project
from core.entities.sequence import Sequence


class ProjectService:
    """Service concerning the project in general."""

    @staticmethod
    def add_sequence_to_project(sequence: Sequence) -> int:
        """Add a Sequence to a Project."""
        _sequence_id = Project.get_next_sequence_id()
        _sequence_dict = Project.get_sequence_dict()
        _sequence_dict[_sequence_id] = sequence
        return _sequence_id