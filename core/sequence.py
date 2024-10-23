"""
The Sequence class holds all the elements that make up a video sequence,
including its video parameters, and the stack of layers it contains
"""

class Sequence:
	unique_id = 0
	
	def __init__(self, project: "Project", name="New sequence", width=1920, height=1080, frame_rate=60, duration=600):
		self.id = Sequence.unique_id 	# int: give a unique id
		self.project = project 			# reference to the project it belongs to
		self.name = name 				# str: sequence's displayed name
		self.width = width 				# int: width in pixels
		self.height = height 			# int: height in pixels
		self.duration = duration 		# int: duration in frames
		self.frame_rate = frame_rate 	# float: frame rate in frames per second
		
		self.layers = dict() 			# dict: indexed set of layers
		self.layer_stack = [] 			# list: orderered stack of layers ids

		Sequence.unique_id += 1 		# increment unique id
	
	# adds a layer to the sequence
	def addLayer(self, layer: "Layer"):
		if layer.id not in self.layers:
			self.layers[layer.id] = layer
			self.layer_stack.append(layer.id)
		
	# TODO : define a rendering method for a sequence's frame