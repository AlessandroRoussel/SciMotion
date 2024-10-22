import sys
from gui.app import App
from core.project import Project

"""
The Main class creates an empty
project and starts the GUI app
"""

class Main:
	def __init__(self):
		self.project = Project() 		# initialize project
		self.app = App(self.project) 	# initialize GUI app
		sys.exit(self.app.exec()) 		# run app

if __name__ == "__main__":
	main = Main()