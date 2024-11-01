"""
A tab for viewing a sequence timeline.

The TimelineTab inherits from QFrame and provides the user with
a visual timeline within the TimelinePane.
"""

from PySide6.QtWidgets import (QFrame, QWidget)

from gui.services.sequence_gui_service import SequenceGUIService


class TimelineTab(QFrame):
    """A tab for viewing a sequence timeline."""

    _sequence_id: int

    def __init__(self, parent: QWidget, sequence_id: int):
        super().__init__(parent)
        self._sequence_id = sequence_id
