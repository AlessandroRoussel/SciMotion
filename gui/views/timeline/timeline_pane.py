"""
A pane for viewing the timeline of a sequence.

The TimelinePane inherits from QFrame and provides the user with
an interactive timeline of the layers making up a sequence.
"""

from PySide6.QtWidgets import (QWidget, QFrame)


class TimelinePane(QFrame):
    """A pane for viewing the timeline of a sequence."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)