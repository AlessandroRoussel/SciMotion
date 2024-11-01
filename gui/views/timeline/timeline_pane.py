"""
A pane for viewing the timelines of sequences.

The TimelinePane inherits from QTabWidget and provides the user
with a tabbed pane for interacting with the timelines of various
sequences. It holds TimelineTab widgets.
"""

from PySide6.QtWidgets import (QWidget, QTabWidget)

from core.entities.project import Project
from gui.views.timeline.timeline_tab import TimelineTab
from gui.services.sequence_gui_service import SequenceGUIService


class TimelinePane(QTabWidget):
    """A pane for viewing the timelines of sequences."""

    _tabs: list[int]  # list(tab id => sequence id)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._tabs = []
        self.setTabsClosable(True)
        SequenceGUIService.open_sequence_signal.connect(self.open_sequence)
        SequenceGUIService.close_sequence_signal.connect(self.close_sequence)
        self.currentChanged.connect(self.on_tab_changed)
        self.tabCloseRequested.connect(self.close_tab)

    def open_sequence(self, sequence_id: int):
        """Open a tab for viewing the timeline of a sequence in the project."""
        if sequence_id in self._tabs:
            _tab_id = self._tabs.index(sequence_id)
            self.setCurrentIndex(_tab_id)
            return
        _sequence = Project.get_sequence_dict()[sequence_id]
        _timeline_tab = TimelineTab(self, sequence_id)
        self._tabs.append(sequence_id)
        self.addTab(_timeline_tab, _sequence.get_title())
        self.setCurrentIndex(len(self._tabs)-1)
    
    def close_sequence(self, sequence_id: int):
        """Close the tab corresponding to a sequence."""
        if sequence_id not in self._tabs:
            return
        _tab_id = self._tabs.index(sequence_id)
        self.close_tab(_tab_id)
    
    def on_tab_changed(self, tab_id: int):
        """Handle the action of switching tab."""
        if tab_id < 0 or tab_id >= len(self._tabs):
            SequenceGUIService.focus_sequence()
            return
        _sequence_id = self._tabs[tab_id]
        SequenceGUIService.focus_sequence(_sequence_id)
        SequenceGUIService.open_sequence_signal.emit(_sequence_id)

    def close_tab(self, tab_id: int):
        """Close a tab."""
        _current_sequence = self._tabs[self.currentIndex()]
        _sequence_id = self._tabs[tab_id]
        self.removeTab(tab_id)
        self._tabs.pop(tab_id)
        SequenceGUIService.close_sequence_signal.emit(_sequence_id)
        if len(self._tabs) == 0:
            SequenceGUIService.focus_sequence()
            return
        if _current_sequence == _sequence_id:
            _current_sequence = self._tabs[self.currentIndex()]
        SequenceGUIService.open_sequence_signal.emit(_current_sequence)
