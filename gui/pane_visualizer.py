from PyQt5.QtWidgets import QFrame, QOpenGLWidget, QVBoxLayout
from OpenGL import GL
import numpy as np

"""
The PaneVisualizer class inherits from QFrame,
it is the video sequence visualization panel
"""

class PaneVisualizer(QFrame):
	def __init__(self, main_window):
		super(QFrame, self).__init__(main_window)
		self.setFrameShape(QFrame.StyledPanel) 		# style the frame
		self.context = GLVisualizer() 				# create an OpenGL context
		self.createGUI() 							# create GUI layout
	
	# create GUI layout
	def createGUI(self):
		layout = QVBoxLayout() 				# create basic layout
		layout.setContentsMargins(0,0,0,0) 	# no margins
		self.setLayout(layout) 				# set layout
		layout.addWidget(self.context) 		# add OpenGL context

"""
The GLVisualizer class inherits from QOpenGLWidget,
it is the OpenGL context used to display the video
sequence within the PaneVisualizer panel
"""

class GLVisualizer(QOpenGLWidget):
	def __init__(self):
		super(QOpenGLWidget, self).__init__()
		self.initTexture()
	
	# sets up OpenGL
	def initializeGL(self):
		# define the clear color to be the Qt5 background color
		qt_color = self.palette().color(self.backgroundRole())
		GL.glClearColor(qt_color.redF(), qt_color.greenF(), qt_color.blueF(), 1)
		
		# enable depth test, 2D textures, and default blend mode
		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glEnable(GL.GL_TEXTURE_2D)
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		
		# create the texture used to display the rendered frames
		self.texture_id = GL.glGenTextures(1)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

	# adapts projection when the panel is resized
	def resizeGL(self, w, h):
		GL.glViewport(0, 0, w, h)
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GL.glOrtho(0, w, 0, h, -1, 1)
		GL.glMatrixMode(GL.GL_MODELVIEW)

	# initializes texture properties
	def initTexture(self):
		self.texture_width = 1 		# texture width in pixels
		self.texture_height = 1 	# texture height in pixels
		self.texture_id = None 		# texture OpenGL id
		self.display = False 		# is there something to display?

	# loads the result from a Renderer object into the texture
	def loadTextureFromRender(self, renderer):
		self.texture_width = renderer.width
		self.texture_height = renderer.height
		image = renderer.getResult()
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F, self.texture_width, self.texture_height, 0, GL.GL_RGBA, GL.GL_FLOAT, image.astype(np.float32).tobytes())
		self.display = True
		self.update()

	# paints the widget
	def paintGL(self):
		# clearing the context
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		
		# draw only if we have a texture loaded up
		if self.display:
			GL.glLoadIdentity()
	
			# draw the texture within a quad of the appropriate dimensions
			half_size = [self.texture_width/2, self.texture_height/2]
			center = [self.width()/2, self.height()/2]
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
	
			GL.glBegin(GL.GL_QUADS)
			GL.glTexCoord2f(0,0); GL.glVertex2f(center[0] - half_size[0], center[1] - half_size[1])
			GL.glTexCoord2f(1,0); GL.glVertex2f(center[0] + half_size[0], center[1] - half_size[1])
			GL.glTexCoord2f(1,1); GL.glVertex2f(center[0] + half_size[0], center[1] + half_size[1])
			GL.glTexCoord2f(0,1); GL.glVertex2f(center[0] - half_size[0], center[1] + half_size[1])
			GL.glEnd()
			
			GL.glFlush()