from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QStatusBar, QSplitter, QWidget, QVBoxLayout, QToolBar

from gui.pane_explorer import PaneExplorer
from gui.pane_miscellaneous import PaneMiscellaneous
from gui.pane_visualizer import PaneVisualizer
from gui.pane_timeline import PaneTimeline
from core.actions import Actions

import params

"""
The MainWindow class inherits from QMainWindow,
it provides the main window for the application
"""

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.windowSettings() 				# setup window
		self.layout = self.createLayout() 	# main pane and basic layout
		panes = self.createPanes() 			# create the main panes
		self.layout.addWidget(panes) 		# add to layout
		self.createToolBar() 				# create tool bar
		self.setStatusBar(QStatusBar(self)) # create status bar
		self.createMenuBar() 				# create menu bar
	
	# center the window on the screen
	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
	
	# setup window
	def windowSettings(self):
		self.setWindowIcon(QIcon("icon.png")) 	# define window icon
		displayedTitle = params.app_title 		# define window title
		displayedTitle += " "+str(params.app_version_major) # add app maj version
		displayedTitle += "."+str(params.app_version_minor) # add app min version
		self.setWindowTitle(displayedTitle) 	# set window title
		self.setMinimumSize(QSize(params.app_min_width, params.app_min_height)) # set minimum window dimensions
	
	# create main pane and basic layout
	def createLayout(self):
		main = QWidget() 					# create main widget
		layout = QVBoxLayout() 				# create simple layout
		layout.setContentsMargins(0,0,0,0) 	# no margins
		main.setLayout(layout) 				# set layout
		self.setCentralWidget(main) 		# set central widget
		return layout
	
	# create the main panes and their layout
	def createPanes(self):
		# main panes
		self.explorer_pane = PaneExplorer(self) 			# project explorer
		self.visualizer_pane = PaneVisualizer(self) 		# sequence visualizer
		self.timeline_pane = PaneTimeline(self) 			# timeline panel
		self.miscellaneous_pane = PaneMiscellaneous(self) 	# miscellaneous
		
		# splitters
		top_pane = QSplitter(Qt.Horizontal)
		left_pane = QSplitter(Qt.Vertical)
		main_pane = QSplitter(Qt.Horizontal)
		
		# set splitter handles thickness
		top_pane.setHandleWidth(params.splitter_width)
		left_pane.setHandleWidth(params.splitter_width)
		main_pane.setHandleWidth(params.splitter_width)
		
		# add panels to splitters
		top_pane.addWidget(self.explorer_pane)
		top_pane.addWidget(self.visualizer_pane)
		left_pane.addWidget(top_pane)
		left_pane.addWidget(self.timeline_pane)
		main_pane.addWidget(left_pane)
		main_pane.addWidget(self.miscellaneous_pane)
		
		# tell the explorer, timeline and miscellaneous
		# panels to not resize with the window
		top_pane.setStretchFactor(0, 0)
		top_pane.setStretchFactor(1, 1)
		left_pane.setStretchFactor(1, 0)
		left_pane.setStretchFactor(0, 1)
		main_pane.setStretchFactor(1, 0)
		main_pane.setStretchFactor(0, 1)
		
		# set default sizes
		top_pane.setSizes([params.left_pane_width, 100])
		left_pane.setSizes([100, params.bottom_pane_height])
		main_pane.setSizes([100, params.right_pane_width])
		
		return main_pane
	
	# create the main tool bar
	def createToolBar(self):
		toolbar = QToolBar("Toolbar")
		self.addToolBar(toolbar)
		# TODO : add tools
	
	# create the main menu bar
	def createMenuBar(self):
		menu = self.menuBar()
		
		# file menu
		menu_file = menu.addMenu("&File")
		menu_file.addAction(self.createAction("New project", Actions.newProject, "Ctrl+N"))
		menu_file.addAction(self.createAction("Open project", Actions.openProject, "Ctrl+O"))
		menu_file.addSeparator()
		menu_file.addAction(self.createAction("Save project", Actions.saveProject, "Ctrl+S"))
		menu_file.addAction(self.createAction("Save project as", Actions.saveProjectAs, "Ctrl+Shift+S"))
		menu_file.addSeparator()
		menu_file.addAction(self.createAction("Project parameters", Actions.projectParameters, "Ctrl+P"))
		menu_file.addSeparator()
		menu_file.addAction(self.createAction("Close project", Actions.closeProject, "Ctrl+Q"))
		
		# edit menu
		menu_edit = menu.addMenu("&Edit")
		menu_edit.addAction(self.createAction("Cut", Actions.cut, "Ctrl+X"))
		menu_edit.addAction(self.createAction("Copy", Actions.copy, "Ctrl+C"))
		menu_edit.addAction(self.createAction("Paste", Actions.paste, "Ctrl+V"))
	
	# create a QAction with a title, shortcut, and triggering a function
	def createAction(self, title, function, shortcut=None):
		action = QAction(title, self)
		action.setStatusTip(title)
		action.triggered.connect(function)
		if(shortcut is not None):
			action.setShortcut(QKeySequence(shortcut))
		return action