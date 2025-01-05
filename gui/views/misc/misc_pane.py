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
from gui.views.misc.layer_properties_panel import LayerPropertiesPanel


class MiscPane(QFrame):
    """A pane for viewing various UI panels."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

        _splitter1 = QSplitter(Qt.Vertical, self)
        _splitter2 = QSplitter(Qt.Vertical, self)

        _layer_properties_panel = LayerPropertiesPanel(self)
        _modifier_list = ModifierList(self)
        _modifier_browser = ModifierBrowser(self)

        _splitter1.addWidget(_splitter2)
        _splitter1.addWidget(_layer_properties_panel)
        _splitter1.setStretchFactor(0, 1)
        _splitter1.setStretchFactor(1, 0)

        _layout.addWidget(_splitter1)
        _splitter2.addWidget(_modifier_list)
        _splitter2.addWidget(_modifier_browser)
        _splitter2.setStretchFactor(0, 1)
        _splitter2.setStretchFactor(1, 0)