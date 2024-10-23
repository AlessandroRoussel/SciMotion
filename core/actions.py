"""
The Actions class defines all the actions that can be
trigerred by a menu, a tool, or a keyboard shortcut
"""

class Actions:
	# TODO : define these actions
	# TODO : add more actions
	
	################
	# file actions #
	################
	def newProject(window: "MainWindow"): 			# create a new project
		print("New project")
		
	def openProject(window: "MainWindow"): 			# open an existing project
		print("Open project")
	
	def saveProject(window: "MainWindow"): 			# save the current project
		print("Save project")
	
	def saveProjectAs(window: "MainWindow"): 			# save the project as a new file
		print("Save project as")
	
	def projectParameters(window: "MainWindow"): 		# open the project parameters
		print("Project parameters")
	
	def close(window: "MainWindow"): 					# close the app
		# TODO : add conditions like saving before closing	
		window.close()
	
	################
	# edit actions #
	################
	def cut(window: "MainWindow"): 					# cut (Ctrl+X)
		print("Cut", window)
		
	def copy(window: "MainWindow"): 					# copy (Ctrl+C)
		print("Copy", window)
		
	def paste(window: "MainWindow"): 					# paste (Ctrl+V)
		print("Paste", window)