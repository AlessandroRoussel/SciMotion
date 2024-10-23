from OpenGL import GL
import numpy as np
import glfw

"""
The RenderEngine class provides an OpenGL rendering context for
dispatching compute shaders and rendering to textures
"""

class RenderEngine():
	def __init__(self):
		self.ready = False 		# bool: is the context ready for rendering
		self.width = 0 			# int: rendering width
		self.height = 0 		# int: rendering height
		self.context = None 	# GLFW window: rendering context
		self.textureA = None 	# OpenGL textureA id
		self.textureB = None 	# OpenGL textureB id

		if not glfw.init():
			raise RuntimeError("Couldn't initialize GLFW")
	
	# destructor
	def __del__(self):
		# TODO : cleanup OpenGL entities
		GL.glDeleteTextures(1, [self.textureA])
		GL.glDeleteTextures(1, [self.textureB])
	
	# create a 2D rgba float32 texture
	def createTexture(self):
		texture_id = GL.glGenTextures(1)
		GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
		GL.glTexStorage2D(GL.GL_TEXTURE_2D, 1, GL.GL_RGBA32F, self.width, self.height)
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
		return texture_id
	
	# create or update the context to the needed dimensions
	def setContextSize(self, width, height):
		if not self.ready or width != self.width or height != self.height:
			
			# clear previous context and textures
			self.clearContextAndTextures()
			self.width = width
			self.height = height
			
			# create an invisible GLFW window as the context
			glfw.window_hint(glfw.VISIBLE, False)
			self.context = glfw.create_window(width, height, "Rendering context", None, None)
			
			if(not self.context):
				glfw.terminate()
				raise RuntimeError("Couldn't create render context")
			
			# use new context
			glfw.make_context_current(self.context)
			
			# create textures A and B
			self.textureA = self.createTexture()
			self.textureB = self.createTexture()
			
			# update ready status
			self.ready = True
	
	# clear the previously existing context and textures
	def clearContextAndTextures(self):
		if self.context:
			glfw.destroy_window(self.context)
		if self.textureA:
			GL.glDeleteTextures(1, [self.textureA])
		if self.textureB:
			GL.glDeleteTextures(1, [self.textureB])
	
	# initialize a texture with an empty image
	def clearTexture(self, texture_id):
	    zeros = np.zeros((self.height, self.width, 4), dtype=np.float32)
	    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
	    GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_FLOAT, zeros)
	    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
	
	# use the engine the render a stack of shaders within a Renderer object
	def render(self, renderer: "Renderer"):
		self.setContextSize(renderer.width, renderer.height)
		self.clearTexture(self.textureA)
		destIsTextureA = renderer.runThrough(self)
		result = self.retrieveData(self.textureA if destIsTextureA else self.textureB)
		renderer.storeResult(result)
	
	# retrieve the image data from the destination texture
	def retrieveData(self, texture_id):
		GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
		data = GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_FLOAT, None)
		image_data = np.frombuffer(data, dtype=np.float32).reshape((self.height, self.width, 4))
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
		return image_data
	
	# bind source and destination textures in alternating order
	def bindTextures(self, destIsTextureA: bool):
		if destIsTextureA:
			GL.glBindImageTexture(0, self.textureA, 0, GL.GL_FALSE, 0, GL.GL_WRITE_ONLY, GL.GL_RGBA32F)
			GL.glBindImageTexture(1, self.textureB, 0, GL.GL_FALSE, 0, GL.GL_READ_ONLY, GL.GL_RGBA32F)
		else:
			GL.glBindImageTexture(0, self.textureB, 0, GL.GL_FALSE, 0, GL.GL_WRITE_ONLY, GL.GL_RGBA32F)
			GL.glBindImageTexture(1, self.textureA, 0, GL.GL_FALSE, 0, GL.GL_READ_ONLY, GL.GL_RGBA32F)