from PyQt5.QtWidgets import QFrame, QOpenGLWidget, QVBoxLayout, QToolBar, QAction, QComboBox, QLineEdit
from PyQt5.QtGui import QWheelEvent, QMouseEvent
from PyQt5.QtCore import Qt
from OpenGL import GL
import numpy as np
import params

"""
The PaneVisualizer class inherits from QFrame,
it is the video sequence visualization panel
"""

class PaneVisualizer(QFrame):
	def __init__(self, main_window: "MainWindow"):
		super(QFrame, self).__init__(main_window)
		self.setFrameShape(QFrame.StyledPanel) 		# style the frame
		self.context = GLVisualizer(self) 			# create an OpenGL context
		self.createGUI() 							# create GUI layout
		
		# TEMPORARY : display a test render
		from render.engine import RenderEngine
		from render.shader import Shader
		from render.renderer import Renderer

		engine = RenderEngine()
		renderer = Renderer(960,540)
		
		shader1 = Shader("linearGradient")
		shader2 = Shader("checkerboard")
		
		renderer.addShader(shader1)
		renderer.addShader(shader2)
		
		engine.render(renderer)
		self.context.linkToRenderer(renderer)
	
	# create GUI layout
	def createGUI(self):
		layout = QVBoxLayout() 				# create basic layout
		layout.setContentsMargins(0,0,0,0) 	# no margins
		layout.setSpacing(0)				# no spacing
		self.setLayout(layout) 				# set layout
		self.createToolBar() 				# create tool bar
		layout.addWidget(self.context) 		# add OpenGL context
		layout.addWidget(self.toolBar) 		# add tool bar
	
	# create the tool bar
	def createToolBar(self):
		self.toolBar = QToolBar("Visualizer toolbar", self)
		
		# zoom drop-down menu
		self.zoomList = QComboBox(self)
		
		self.zoomList.addItem("Fit to frame")
		self.zoomList.addItem("Fit up to 100%")
		
		self.zoomList.insertSeparator(2)
		
		self.zoomList.addItem("50%")
		self.zoomList.addItem("100%")
		self.zoomList.addItem("200%")
		
		self.zoomList.currentIndexChanged.connect(self.chooseZoom)
		self.zoomList.setCurrentIndex(4)
		self.zoomListLength = self.zoomList.count()
		
		self.toolBar.addWidget(self.zoomList)
		
		# tool bar styling
		self.toolBar.setOrientation(Qt.Horizontal)
	
	# remove custom zoom option
	def removeCustomZoom(self):
		self.zoomList.blockSignals(True)
		if self.zoomList.count() > self.zoomListLength:
			self.zoomList.removeItem(self.zoomListLength)
	
	# update the displayed zoom value
	def updateZoomValue(self, zoom):
		self.removeCustomZoom()
		text = str(round(zoom*100))+"%"
		if self.zoomList.findText(text) == -1:
			self.zoomList.addItem(text)
			self.zoomList.setCurrentIndex(self.zoomListLength)
		self.zoomList.blockSignals(False)
	
	# zoom drop-down menu options
	def chooseZoom(self, index):
		self.removeCustomZoom()
		
		# execute chosen option
		if index == 0:
			self.context.fitToFrame()
		elif index == 1:
			self.context.fitToFrame(max_zoom=1)
		elif index == 3:
			self.context.chooseZoom(.5)
		elif index == 4:
			self.context.chooseZoom(1)
		elif index == 5:
			self.context.chooseZoom(2)


"""
The GLVisualizer class inherits from QOpenGLWidget,
it is the OpenGL context used to display the video
sequence within the PaneVisualizer panel
"""

class GLVisualizer(QOpenGLWidget):
	def __init__(self, pane: PaneVisualizer):
		super(QOpenGLWidget, self).__init__()		
		self.pane = pane 			# parent PaneVisualiser
		
		self.renderer = None 		# Renderer object to display
		self.texture_ready = False 	# is the rendered texture loaded
		self.ready = False 			# is the context ready to display
		self.texture_id = None 		# OpenGL texture's id
		self.program = None 		# shader program
		self.VAO = None 			# vertex array object
		self.VBO = None 			# vertex buffer object
		self.EBO = None 			# elements buffer object
		
		self.texture_width = 0 		# texture width in pixels
		self.texture_height = 0 	# texture height in pixels
		self.center_x = 0 			# which pixel is centered x-position
		self.center_y = 0 			# which pixel is centered y-position
		self.zoom = 1 				# viewing zoom factor
		self.checkerboard = True 	# transparency as checkerboard
		
		self.mouse_middle_dragging = False 	# middle mouse button dragging
		self.mouse_last_position = None 	# QPoint: last mouse position
		self.fitting_zoom = False 			# has the user chosen to fit
		self.fitting_zoom_max = None 		# maximum zoom for fitting
	
	# destructor
	def __del__(self):
		# TODO : cleanup OpenGL entities
		GL.glDeleteTextures(1, [self.texture_id])
		GL.glDeleteVertexArrays(1, [self.VAO])
		GL.glDeleteBuffers(1, [self.VBO])
		GL.glDeleteBuffers(1, [self.EBO])
	
	##############
	# displaying #
	##############
	
	# sets up OpenGL
	def initializeGL(self):
		# define the clear color to be the Qt5 background color
		qt_color = self.palette().color(self.backgroundRole())
		GL.glClearColor(qt_color.redF(), qt_color.greenF(), qt_color.blueF(), 1)
		
		# default blending mode
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		
		self.initShader() 		# initialize shader
		self.setupQuad() 		# initialize quad
		self.initTexture() 		# initialize texture
		self.ready = True 		# update status

	# adapts projection when the panel is resized
	def resizeGL(self, w, h):
		GL.glViewport(0, 0, w, h)
		
		# fit to frame if fitting is enabled
		if self.fitting_zoom:
			self.fitToFrame(self.fitting_zoom_max, False)
	
	# creates shader program
	def initShader(self):
		# basic vertex shader code
		vertex_code = """#version 430
		layout (location = 0) in vec2 aPos;
		layout (location = 1) in vec2 aTexCoord;
		out vec2 texCoord;
		uniform mat4 u_transform;
		void main(){
			gl_Position = u_transform * vec4(aPos,0.,1.);
			texCoord = aTexCoord;
		}"""
		
		# basic fragment shader code
		# composites the texture onto either a black background
		# or a checkerboard texture
		fragment_code = """#version 430
		in vec2 texCoord;
		out vec4 fragColor;
		uniform sampler2D u_texture;
		uniform bool u_checkerboard;
		uniform vec2 u_dimensions;
		
		// default checkerboard background
		float checkerTexture(vec2 xy){
			float size = """+"{0:.2f}".format(params.checkerboard_size)+""";
			vec2 q = xy/size-2.*floor(xy/2./size);
			return mix("""+"{0:.2f}".format(params.checkerboard_color_a)+""",
			  """+"{0:.2f}".format(params.checkerboard_color_b)+""",
			  float(q.x < 1. ^^ q.y < 1.));
		}
		
		void main(){
			vec4 color = texture(u_texture,texCoord);
			vec3 backColor = vec3(0.);
			if(u_checkerboard){
					vec2 checkerboardCoord = gl_FragCoord.xy - u_dimensions*.5;
				backColor = vec3(checkerTexture(checkerboardCoord));
			}
			vec3 blendedColor = mix(backColor, color.rgb, color.a);
			fragColor = vec4(blendedColor, 1.);
		}"""
		
		# compile vertex shader
		vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
		GL.glShaderSource(vertex_shader, vertex_code)
		GL.glCompileShader(vertex_shader)
	
		# compile fragment shader
		fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
		GL.glShaderSource(fragment_shader, fragment_code)
		GL.glCompileShader(fragment_shader)
	
		# link shaders into a program
		self.program = GL.glCreateProgram()
		GL.glAttachShader(self.program, vertex_shader)
		GL.glAttachShader(self.program, fragment_shader)
		GL.glLinkProgram(self.program)
	
		# clean up shaders
		GL.glDeleteShader(vertex_shader)
		GL.glDeleteShader(fragment_shader)
	
	# initializes vertex array
	def setupQuad(self):
		# define quad vertices for the quad (position + tex coords)
		vertices = np.array([
			-1, -1, 0, 0,
			1, -1, 1, 0,
			1, 1, 1, 1,
			-1, 1, 0, 1], dtype=np.float32)

		# define quad triangles
		indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
		
		# generate vertex array
		self.VAO = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.VAO)
		
		# generate and bind vertex buffer
		self.VBO = GL.glGenBuffers(1)
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
		
		# generate and bind element buffer
		self.EBO = GL.glGenBuffers(1)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)
		
		# position attribute
		GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * vertices.itemsize, GL.ctypes.c_void_p(0))
		GL.glEnableVertexAttribArray(0)

		# texture coordinate attribute
		GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * vertices.itemsize, GL.ctypes.c_void_p(2 * vertices.itemsize))
		GL.glEnableVertexAttribArray(1)

		# unbind vertex array
		GL.glBindVertexArray(0)

	# initializes texture properties
	def initTexture(self):	
		# create the texture used to display the rendered frames
		self.texture_id = GL.glGenTextures(1)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
		
		# setup OpenGL texture parameters
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
		GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
		
		# unbind texture
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

	# link this display to a Renderer object
	def linkToRenderer(self, renderer: "Renderer"):
		self.renderer = renderer
		self.texture_width = renderer.width
		self.texture_height = renderer.height
		self.centerInFrame()
		self.update()
	
	# change the zoom value
	def setZoom(self, value):
		self.zoom = max(params.min_zoom,min(value, params.max_zoom))
	
	# center the texture in the frame
	def centerInFrame(self):
		self.center_x = self.texture_width/2
		self.center_y = self.texture_height/2

	# loads the result from the Renderer object into the texture
	def loadTextureFromRender(self):
		image = self.renderer.getResult()
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F, self.renderer.width, self.renderer.height, 0, GL.GL_RGBA, GL.GL_FLOAT, image.astype(np.float32).tobytes())
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
		self.texture_ready = True

	# gives the transformation matrix to resize the viewed texture
	def getTransformationMatrix(self):
		# widget dimensions
		width = self.width()
		height = self.height()
		
		# scale factor
		scale_x = self.zoom * self.texture_width / width
		scale_y = self.zoom * self.texture_height / height
		
		# offset
		offset_x = self.zoom * (self.texture_width - 2*self.center_x) / width
		offset_y = self.zoom * (- self.texture_height + 2*self.center_y) / height

		# transformation matrix
		transform = np.array([
			[scale_x,0,0,offset_x],
			[0,scale_y,0,offset_y],
			[0,0,1,0],
			[0,0,0,1]
		], dtype=np.float32)
		return transform

	# paints the widget
	def paintGL(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT)
		if self.ready and self.renderer is not None and self.renderer.rendered:
			if not self.texture_ready:
				self.loadTextureFromRender()
		
			# use shader and VAO
			GL.glUseProgram(self.program)
			GL.glBindVertexArray(self.VAO)
			
			# set transformation matrix
			transform = self.getTransformationMatrix()
			transform_loc = GL.glGetUniformLocation(self.program, "u_transform")
			GL.glUniformMatrix4fv(transform_loc, 1, GL.GL_TRUE, transform)
			
			# bind texture
			GL.glActiveTexture(GL.GL_TEXTURE0)
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
			GL.glUniform1i(GL.glGetUniformLocation(self.program, "u_texture"), 0)
			
			# pass additional uniforms
			GL.glUniform1i(GL.glGetUniformLocation(self.program, "u_checkerboard"), self.checkerboard)
			GL.glUniform2f(GL.glGetUniformLocation(self.program, "u_dimensions"), self.width(), self.height())
	
			# draw the quad
			GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
			
			# unbind texture, VAO and program
			GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
			GL.glBindVertexArray(0)
			GL.glUseProgram(0)
	
	
	##################
	# event handling #
	##################
	
	# converts widget space to image space
	def widgetToImageXY(self, widget_x, widget_y):
		img_x = (widget_x - self.width()/2) / self.zoom + self.center_x
		img_y = (widget_y - self.height()/2) / self.zoom + self.center_y
		return img_x, img_y
	
	# converts image space to widget space
	def imageToWidgetXY(self, img_x, img_y):
		widget_x = (img_x - self.center_x) * self.zoom + self.width()/2
		widget_y = (img_y - self.center_y) * self.zoom + self.height()/2
		return widget_x, widget_y
	
	# handle the wheel scroll event
	def wheelEvent(self, event: QWheelEvent):
		self.onWheelScroll(event.angleDelta().y(), event.pos())
	
	# handle the mouse press event
	def mousePressEvent(self, event: QMouseEvent):
		if event.button() == Qt.MiddleButton:
			self.mouse_middle_dragging = True
			self.mouse_last_position = event.pos()
			self.setCursor(Qt.ClosedHandCursor)
	
	# handle the mouse release event
	def mouseReleaseEvent(self, event: QMouseEvent):
		if event.button() == Qt.MiddleButton:
			self.mouse_middle_dragging = False
			self.setCursor(Qt.ArrowCursor)
	
	# handle the mouse move event
	def mouseMoveEvent(self, event: QMouseEvent):
		if self.mouse_middle_dragging:
			current_pos = event.pos()
			delta = current_pos - self.mouse_last_position
			self.onMiddleMouseDrag(delta)
			self.mouse_last_position = current_pos

	# function triggered when the wheel is scrolled
	def onWheelScroll(self, delta, mouse_pos):		
		# calculate the cursor position in the image space
		img_x, img_y = self.widgetToImageXY(mouse_pos.x(), mouse_pos.y())
		
		# change zoom factor
		factor = np.exp(delta / 100. * params.zoom_sensitivity)
		self.setZoom(self.zoom * factor)
		
		if params.zoom_around_cursor:
			# update position to lock the image under the cursor
			self.center_x = img_x - (img_x - self.center_x)/factor
			self.center_y = img_y - (img_y - self.center_y)/factor
		
		self.fitting_zoom = False 	# stop fitting to frame
		self.parent().updateZoomValue(self.zoom) # update zoom display
		self.update() 				# update visualizer
	
	# function triggered when the wheel is scrolled
	def onMiddleMouseDrag(self, delta):
		# move image within visualizer
		self.center_x -= delta.x() / self.zoom
		self.center_y -= delta.y() / self.zoom
		
		self.update() 	# update visualizer
	
	# fit the viewer to the frame
	def fitToFrame(self, max_zoom=None, update=True):
		# move image to center
		self.centerInFrame()
		
		# maximize zoom up to 100%
		padding = params.viewer_fit_padding
		width = self.width() - 2*padding
		height = self.height() - 2*padding
		zoom = min(width/self.texture_width, height/self.texture_height)
		if max_zoom is not None:
			zoom = min(zoom, max_zoom)
		self.setZoom(zoom)
		
		# change fitting status
		self.fitting_zoom = True
		self.fitting_zoom_max = max_zoom
		
		if update:
			self.update() 	# update visualizer
	
	# user chooses the zoom
	def chooseZoom(self, value):
		self.setZoom(value) 		# set zoom value
		self.fitting_zoom = False 	# stop fitting to frame
		self.update() 				# update visualizer
		self.pane.updateZoomValue(self.zoom) # update zoom display