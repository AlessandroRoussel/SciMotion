"""A set of services for dialogs."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QDialog)


class DialogService:
    """A set of services for dialogs."""

    @staticmethod
    def add_input(dialog: QDialog,
                  layout: QBoxLayout,
                  label: str,
                  input: QWidget,
                  suffix: str = ""):
        """Insert an input into a dialog, with title and suffix labels."""
        _input_layout = QHBoxLayout()
        _input_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        _name_label = QLabel(f"{label}:", dialog)
        _name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _name_label.setFixedWidth(100)

        _input_layout.addWidget(_name_label)
        _input_layout.addWidget(input)

        if suffix.strip() != "":
            _suffix_label = QLabel(f"{suffix.strip()}", dialog)
            _suffix_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            _input_layout.addWidget(_suffix_label)

        layout.addLayout(_input_layout)
    
    @staticmethod
    def add_ok_cancel(dialog: QDialog,
                      layout: QBoxLayout,
                      ok_text: str = "OK",
                      cancel_text: str = "Cancel"):
        """Insert OK and Cancel buttons into a dialog."""
        _button_layout = QHBoxLayout()
        _cancel_button = QPushButton(cancel_text, dialog)
        _ok_button = QPushButton(ok_text, dialog)
        _cancel_button.clicked.connect(dialog.reject)
        _ok_button.clicked.connect(dialog.accept)
        _button_layout.addStretch()
        _button_layout.addWidget(_cancel_button)
        _button_layout.addWidget(_ok_button)
        layout.addLayout(_button_layout)
        _ok_button.setDefault(True)