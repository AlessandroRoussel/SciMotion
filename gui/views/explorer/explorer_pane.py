"""
A pane for exploring media files and sequences.

The ExplorerPane inherits from QFrame and provides the user with
an interactive tree of all files and sequences within the project.
"""

from PySide6.QtWidgets import (QWidget, QFrame)


class ExplorerPane(QFrame):
    """A pane for viewing images and video sequences."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)