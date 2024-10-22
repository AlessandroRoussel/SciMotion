"""
The Color class provides a utilitary Color object
to manage color transformations, blending modes...
"""

class Color:
	def __init__(self, red=0, green=0, blue=0, alpha=0):
		self.red = red 			# float: red component
		self.green = green 		# float: green component
		self.blue = blue 		# float: blue component
		self.alpha = alpha 		# float: alpha component
		
	# TODO : define operators and functions