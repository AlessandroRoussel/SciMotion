from core.parameter import Parameter
from OpenGL import GL
import json
import os

"""
The Shader class represent a visual effects that the user can
apply to a layer. It contains a compute shader program meant
to run on GPU, along with some parameters that can be passed
to the program. For a shader with identifier *id*, the GLSL
compute shader code is stored in "shaders/*id*.glsl", and
the JSON file containing all its parameters and settings
is stored in "shaders/*id*.info".
"""

class Shader:
	def __init__(self, id):
		self.id = id 			# str: unique identifier
		self.loaded = False 	# bool: files loading status
		self.compiled = False 	# bool: program compiling status
		
		self.program = None 	# OpenGL shader program
		self.code = None 		# str: shader GLSL code
		self.info = None 		# dict: shader info unpacked JSON
		
		self.name = "" 					# str: displayed name
		self.parameters = [] 			# list: list of Parameter objects
		self.parametersIds = dict() 	# dict(str:int) dict of indices
		self.flags = set() 				# set of flags
		
		self.loadShader() 		# load in the shader files
	
	# loads the GLSL code (shaders/*id*.glsl)
	def loadShaderCode(self):
		path = os.path.join("shaders", self.id+".glsl")
		with open(path, "r") as file:
			return file.read()
	
	# loads the JSON info (shaders/*id*.info)
	def loadShaderInfo(self):
		path = os.path.join("shaders", self.id+".info")
		with open(path, "r") as file:
			return json.load(file)
	
	# transfer the info from the JSON to instance's attributes
	def unpackInfo(self):
		if "name" in self.info:
			self.name = str(self.info["name"])
		if "flags" in self.info:
			self.flags = set(self.info["flags"])
		if "parameters" in self.info:
			for param in self.info["parameters"]:
				parameter = Parameter(**param)
				self.parametersIds[parameter.identifier] = len(self.parameters)
				self.parameters.append(parameter)
	
	# checks if the shader exhibits a flag
	def hasFlag(self, flag):
		return flag in self.flags
	
	# load the shader files
	def loadShader(self):
		self.code = self.loadShaderCode() 	# load the GLSL code
		self.info = self.loadShaderInfo() 	# load the JSON info
		self.compiled = False 				# asks to compile again
		self.loaded = True 					# files loaded
		self.unpackInfo() 					# extract info from JSON
		
	# compile the shader program
	def compileShader(self):
		if not self.loaded:
			print("Shader not loaded")
			return
		
		# create and compile shader
		shader = GL.glCreateShader(GL.GL_COMPUTE_SHADER)
		GL.glShaderSource(shader, self.code)
		GL.glCompileShader(shader)
		
		# create and link program
		self.program = GL.glCreateProgram()
		GL.glAttachShader(self.program, shader)
		GL.glLinkProgram(self.program)
		
		# update compilation status
		self.compiled = True
	
	# checks if the shader is ready to be used
	def ready(self):
		return self.loaded and self.compiled
	
	# apply the shader program using a RenderEngine
	def dispatch(self, engine):
		GL.glUseProgram(self.program)
		GL.glDispatchCompute(engine.width, engine.height, 1)
		GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
	
	# change the value of a parameter
	# TODO : place this in the Parameter class instead
	def setParameter(self, identifier, value):
		if identifier not in self.parametersIds:
			print("Parameter "+str(identifier)+" doesn't exist")
			return
		paramId = self.parametersIds[identifier]
		self.parameters[paramId].setValue(value)
	
	# passes the parameters to the program using uniforms
	def setUniforms(self):
		GL.glUseProgram(self.program)
		
		for parameter in self.parameters:
			location = GL.glGetUniformLocation(self.program, parameter.identifier)
			value = parameter.getValue()
			
			if parameter.data_type == "float":
				if parameter.dimension == 1:
					GL.glUniform1f(location, value[0])
				elif parameter.dimension == 2:
					GL.glUniform2f(location, value[0], value[1])
				elif parameter.dimension == 3:
					GL.glUniform3f(location, value[0], value[1], value[2])
				elif parameter.dimension == 4:
					GL.glUniform4f(location, value[0], value[1], value[2], value[3])
			
			if parameter.data_type == "int":
				if parameter.dimension == 1:
					GL.glUniform1i(location, value[0])
				elif parameter.dimension == 2:
					GL.glUniform2i(location, value[0], value[1])
				elif parameter.dimension == 3:
					GL.glUniform3i(location, value[0], value[1], value[2])
				elif parameter.dimension == 4:
					GL.glUniform4i(location, value[0], value[1], value[2], value[3])
			
			if parameter.data_type == "bool":
				if parameter.dimension == 1:
					GL.glUniform1b(location, value[0])
				elif parameter.dimension == 2:
					GL.glUniform2b(location, value[0], value[1])
				elif parameter.dimension == 3:
					GL.glUniform3b(location, value[0], value[1], value[2])
				elif parameter.dimension == 4:
					GL.glUniform4b(location, value[0], value[1], value[2], value[3])