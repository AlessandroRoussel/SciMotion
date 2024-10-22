from PyQt5.QtWidgets import QFrame

"""
The PaneTimeline class inherits from QFrame,
it is the timeline editing panel
"""

class PaneTimeline(QFrame):
	def __init__(self, main_window):
		super(QFrame, self).__init__(main_window)
		self.setFrameShape(QFrame.StyledPanel) 		# style the frame
	
	