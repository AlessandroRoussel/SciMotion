import numpy as np

"""
The Parameter class represents a value that the user can edit
in order to affect the state of a layer or a visual effect.
It can be of various types (float, int, bool), and dimensions
in order to represent various types of data (positions, colors...)
"""

class Parameter:
	# allowed data-types
	data_types = {
		"float": np.float32,
		"int": int,
		"bool": bool
	}
	
	def __init__(self, identifier="", name="", data_type="float", dimension=1, default_value=0, min_value=None, max_value=None):
		self.identifier = identifier 		# str: unique parameter's name
		self.name = name 					# str: parameter's displayed name
		
		# check if data-type is allowed
		if data_type not in Parameter.data_types.keys():
			raise TypeError(f"Unknown parameter data-type: {data_type}")
		
		self.dimension = dimension 			# int: array size
		self.data_type = data_type 			# str: name of data-type (float, int, bool)
		
		self.value = None 					# current value of the parameter
		self.min_value = None 				# minimum value of the parameter (can be an array)
		self.max_value = None 				# maximum value of the parameter (can be an array)
		
		# set minimum, maximum, and default values
		self.setMinMaxDef(min_value, max_value, default_value)
		self.setValue(default_value)
	
	# set the value of the parameter
	def setValue(self, value):
		self.value = self.conform(value)
	
	# retrieve the value of the parameter
	def getValue(self):
		return self.value
	
	# set the minimum, maximum, and default values for the parameter
	def setMinMaxDef(self, min_value, max_value, default_value):
		if min_value is not None:
			self.min_value = self.conformToType(min_value)
		if max_value is not None:
			self.max_value = self.conformToType(max_value)
		self.default_value = self.conform(default_value)
	
	# format a value to be of the correct data-type,
	# in a numpy vector with the appropriate dimension
	def conformToType(self, value):
		ret = np.array(0, dtype=Parameter.data_types[self.data_type])
		ret = np.array(value, dtype=Parameter.data_types[self.data_type])
		if len(ret.shape) == 0:
			ret = np.full(self.dimension, ret, dtype=ret.dtype)
		return ret
	
	# format a value to be of the correct data-type,
	# and clamped between the min and max values
	def conform(self, value):
		array = self.conformToType(value)
		if self.min_value is not None:
			array = np.maximum(array, self.min_value)
		if self.max_value is not None:
			array = np.minimum(array, self.max_value)
		return array