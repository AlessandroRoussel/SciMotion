from PyQt5.QtWidgets import QFrame, QTreeWidget, QVBoxLayout, QApplication, QTreeWidgetItem
from tools.time import Time

"""
The PaneExplorer class inherits from QFrame, it displays
a structured tree of the project's sequences and media
"""

class PaneExplorer(QFrame):
	def __init__(self, main_window):
		super(QFrame, self).__init__(main_window)
		self.setFrameShape(QFrame.StyledPanel) 		# style the frame
		self.tree = QTreeWidget() 					# tree widget
		self.createGUI() 							# create GUI
		self.buildTree() 							# build tree
	
	# creates the GUI layout and the explorer tree
	def createGUI(self):
		# create simple layout
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		# define the columns of the explorer
		self.tree.setColumnCount(4)
		self.tree.setHeaderLabels(["Name", "Resolution", "Duration", "Frame rate"])

		# setup the widths of the columns
		self.tree.setColumnWidth(0, 150)
		self.tree.setColumnWidth(1, 120)
		self.tree.setColumnWidth(2, 100)
		self.tree.setColumnWidth(3, 50)
		self.tree.setIndentation(0)
		
		# add tree to layout
		layout.addWidget(self.tree)
	
	# builds the tree from the project's data
	def buildTree(self):
		# TODO : find a better way to access the project's data
		project = QApplication.instance().project
		
		# construct a list of all sequences with their details
		sequences = []
		for seqid, seq in project.sequences.items():
			item = QTreeWidgetItem([
							seq.name,
							str(seq.width)+"x"+str(seq.height)+"px",
							Time.formatTime(seq.duration, seq.frame_rate),
							str(seq.frame_rate)+"i/s"])
			sequences.append(item)
		
		# insert the data and display the tree
		self.tree.insertTopLevelItems(0, sequences)
		self.tree.show()