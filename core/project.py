"""
The Project class holds all the elements that make up a video project,
including the set of all video sequences, and all external media files
"""

class Project:
	def __init__(self, name="Untitled project"):
		self.name = name 			# str: project's displayed name
		self.sequences = dict() 	# dict: indexed set of sequences
		self.media_library = dict() # dict: indexed set of media
		
		# TODO : dynamical creation of sequences using menus
		# TEMPORARY : add a sequence
		from core.sequence import Sequence
		sequence = Sequence(self)
		self.addSequence(sequence)
	
	# adds sequence to the project environment
	def addSequence(self, sequence: "Sequence"):
		if sequence.id not in self.sequences:
			self.sequences[sequence.id] = sequence