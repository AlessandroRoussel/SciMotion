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
	def newProject(s): 					# create a new project
		print("New project", s)
		
	def openProject(s): 				# open an existing project
		print("Open project", s)
	
	def saveProject(s): 				# save the current project
		print("Save project", s)
	
	def saveProjectAs(s): 				# save the project as a new file
		print("Save project as", s)
	
	def projectParameters(s): 			# open the project parameters
		print("Project parameters", s)
	
	def closeProject(s): 				# close the current project
		print("Close project", s)
	
	################
	# edit actions #
	################
	def cut(s): 				# cut (Ctrl+X)
		print("Cut", s)
		
	def copy(s): 				# copy (Ctrl+C)
		print("Copy", s)
		
	def paste(s): 				# paste (Ctrl+V)
		print("Paste", s)