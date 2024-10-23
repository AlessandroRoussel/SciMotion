from PyQt5.QtWidgets import QFrame

"""
The PaneMiscellaneous class inherits from QFrame,
it is a pane containing various useful elements
"""

class PaneMiscellaneous(QFrame):
	def __init__(self, main_window: "MainWindow"):
		super(QFrame, self).__init__(main_window)
		self.setFrameShape(QFrame.StyledPanel) 		# style the frame
	