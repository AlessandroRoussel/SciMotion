"""
The application class.

The class App represents the QApplication
used within PyQt5 to create the GUI app.
"""

from PyQt5.QtWidgets import QApplication


class App(QApplication):
    """The application class."""

    def __init__(self):
        super().__init__([])
