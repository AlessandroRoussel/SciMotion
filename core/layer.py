"""
The Layer class holds all the elements that make up a video layer,
including its type (solid color, media, effects layer, text layer...),
its transformation parameters (position, rotation, scale, opacity...),
and the stack of effects that are applied to it
"""

class Layer:
	
	unique_id = 0
	
	def __init__(self, sequence, name="New layer", width=1920, height=1080, start_frame=0, end_frame=600):
		self.id = Layer.unique_id 		# int: give a unique id
		self.sequence = sequence 		# reference to the sequence it belongs to
		self.name = name 				# str: layer's displayed name
		self.width = width 				# int: width in pixels
		self.height = height 			# int: height in pixels
		self.start_frame = start_frame 	# int: starting frame
		self.end_frame = end_frame 		# int: ending frame
		
		Layer.unique_id += 1 			# increment unique id
	
	# TODO : implement different types of layers
	# TODO : add transformation parameters
	# TODO : add effects stack
	# TODO : define a rendering method for a layer