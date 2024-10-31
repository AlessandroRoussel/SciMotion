"""
A pane for exploring media files and sequences.

The ExplorerPane inherits from QFrame and provides the user with
an interactive tree of all files and sequences within the project.
"""

from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout)

from gui.views.explorer.sequence_browser import SequenceBrowser


class ExplorerPane(QFrame):
    """A pane for viewing images and video sequences."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        _sequence_browser = SequenceBrowser(self)

        _layout.addWidget(_sequence_browser)