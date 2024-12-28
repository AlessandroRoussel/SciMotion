from PySide6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class DraggableFloatInput(QLineEdit):
    def __init__(self, initial_value=0.0, step=0.1, parent=None):
        super().__init__(parent)
        self.setText(f"{initial_value}")
        self.setAlignment(Qt.AlignCenter)
        self.step = step
        self.value = initial_value
        self.last_mouse_position = None
        self.setFocusPolicy(Qt.TabFocus)
        self.setCursor(Qt.SizeHorCursor)

        highlight_color = QApplication.palette().accent().color()
        color_rgb = (f"rgb({highlight_color.red()},"
                     f"{highlight_color.green()},"
                     f"{highlight_color.blue()})")
        self.setStyleSheet(f"""
            QLineEdit {{
                padding: 2px;
                border-radius: 0;
                border: none;
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 0;
                color: {color_rgb};
            }}
            QLineEdit:hover {{
                border-bottom: 1px solid {color_rgb};
            }}
            QLineEdit:focus {{
                border-radius: 3px;
                border: 1px solid {color_rgb};
            }}
            """)
        
        self.textEdited.connect(self.onUserInput)
        self.textChanged.connect(self.updateWidth)
        self.updateWidth()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.hasFocus():
                self.last_mouse_position = event.globalPosition().toPoint()
                self.start_value = self.value
                self.setFocus()
                self.clearFocus()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            delta = event.globalPosition().toPoint() - self.last_mouse_position
            self.value += delta.x() * self.step
            self.setText(f"{self.value:.2f}")
            self.last_mouse_position = event.globalPosition().toPoint()
            self.clearFocus()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.hasFocus():
                self.last_mouse_position = None
                if self.start_value == self.value:
                    self.selectAll()
                    self.setFocus()
                    self.setCursor(Qt.IBeamCursor)
            else:
                super().mouseReleaseEvent(event)
    
    def onUserInput(self):
        try:
            self.value = float(self.text())
        except ValueError:
            self.setText(f"{self.value:.2f}")
    
    def updateWidth(self):
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        self.setFixedWidth(text_width + 12)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        self.setCursor(Qt.SizeHorCursor)
        super().focusOutEvent(event)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draggable Float Input")
        layout = QVBoxLayout(self)
        self.float_input = DraggableFloatInput(0.0, step=0.1)
        layout.addWidget(self.float_input)
        self.float_input2 = DraggableFloatInput(0.0, step=0.1)
        layout.addWidget(self.float_input2)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()