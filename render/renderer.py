"""
The Renderer class stores a stack of shaders which can
be rendered using a RenderEngine object. It then stores
the result of this render.
"""

class Renderer:
	def __init__(self, width, height):
		self.width = width 		# int: image width
		self.height = height 	# int: image height
		self.shader_list = [] 	# stack of shaders
		self.result = None 		# rendered image data
		self.rendered = False 	# rendering status
		self.stack_start = 0 	# shaders to skip
	
	# adds a shader at the bottom of the stack
	def addShader(self, shader):
		if shader.hasFlag("WRITEONLY"):
			# if the shader exhibits the WRITEONLY flag,
			# we skip all previous shaders, because its
			# result won't depend on theirs
			self.stack_start = len(self.shader_list)
		self.shader_list.append(shader)
	
	# applies all shaders in order using a RenderEngine
	def runThrough(self, engine):
		# we use a ping-pong method with two textures alternating
		# between being the source or the destination texture
		destIsTextureA = True
		for shader in self.shader_list[self.stack_start:]:
			
			if not shader.ready(): 					# compile shader if needed
				shader.compileShader()
			
			shader.setUniforms() 					# pass uniforms to shader
			engine.bindTextures(destIsTextureA) 	# bind src and dest textures
			shader.dispatch(engine) 				# execute the shader

			destIsTextureA = not destIsTextureA 	# swap src and dest textures
		
		# return which texture is the last destination (True if textureA)
		return not destIsTextureA
	
	# stores the rendered image
	def storeResult(self, data):
		self.result = data
		self.rendered = True
	
	# retrieve the rendered image
	def getResult(self):
		return self.result