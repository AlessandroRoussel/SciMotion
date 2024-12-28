"""
A pane for viewing various UI panels.

The MiscPane inherits from QFrame and provides the user with
many different panels for useful operations, such as browsing
modifiers, viewing audio levels...
"""

from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QSplitter)
from PySide6.QtCore import Qt

from gui.views.misc.modifier_browser import ModifierBrowser
from gui.views.misc.modifier_list import ModifierList


class MiscPane(QFrame):
    """A pane for viewing various UI panels."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        _splitter = QSplitter(Qt.Vertical, self)

        _modifier_list = ModifierList(self)
        _modifier_browser = ModifierBrowser(self)

        _layout.addWidget(_splitter)
        _splitter.addWidget(_modifier_list)
        _splitter.addWidget(_modifier_browser)
        _splitter.setStretchFactor(0, 1)
        _splitter.setStretchFactor(1, 0)