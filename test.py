import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QSurfaceFormat, QVector4D, QOpenGLContext
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import (QOpenGLWindow, QOpenGLVertexArrayObject, QOpenGLBuffer,
                              QOpenGLShaderProgram, QOpenGLShader)
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import OpenGL.GL as pygl
from shiboken6 import VoidPtr

import moderngl
import numpy as np
import ctypes

class TriangleGL(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()

        # some vertex data for corners of triangle
        self.vertexData = np.array(
            [-0.5, -0.5, 0.0,  # x, y, z
             0.5, -0.5, 0.0,  # x, y, z
             0.0, 0.5, 0.0],  # x, y, z
            dtype=ctypes.c_float
        )
        # triangle color
        self.triangleColor = QVector4D(0.5, 0.5, 0.0, 0.0)  # yellow triangle
        # notice the correspondance the vec4 of fragment shader 
        # and our choice here

    def getGlInfo(self):
        "Get opengl info"
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
            pygl.glGetString(pygl.GL_VENDOR),
            pygl.glGetString(pygl.GL_RENDERER),
            pygl.glGetString(pygl.GL_VERSION),
            pygl.glGetString(pygl.GL_SHADING_LANGUAGE_VERSION)
        )
        return info

    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())
        # create context and make it current
        self.context.create()
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)
            
        # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(1, 0, 0, 1)

        # deal with shaders
        vshader = """
        in vec3 aPos;
        out vec2 TexCoord;

        void main(void)
        {
            gl_Position = vec4(aPos, 1.0);
            TexCoord = aPos.xy;
        }
        """
        fshader = """
        uniform vec4 color;
        in vec2 TexCoord;

        void main(void)
        {
            gl_FragColor = vec4(TexCoord,0.,1.);
        }
        """

        # creating shader program
        self.program = QOpenGLShaderProgram(self.context)
        vertex = QOpenGLShader(QOpenGLShader.Vertex)
        fragment = QOpenGLShader(QOpenGLShader.Fragment)
        vertex.compileSourceCode(vshader)
        fragment.compileSourceCode(fshader)
        self.program.addShader(vertex)  # adding vertex shader
        self.program.addShader(fragment)  # adding fragment shader

        # bind attribute to a location
        self.program.bindAttributeLocation(self.program.uniformLocation("aPos"))

        # link shader program
        isLinked = self.program.link()
        print("shader program is linked: ", isLinked)

        # bind the program
        self.program.bind()

        # specify uniform value
        colorLoc = self.program.uniformLocation("color")
        self.program.setUniformValue(colorLoc,
                                     self.triangleColor)

        # self.useShader("triangle")

        # deal with vao and vbo

        # create vao and vbo

        # vao
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        # vbo
        isVbo = self.vbo.create()
        isBound = self.vbo.bind()

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on buffer
        self.vbo.allocate(self.vertexData.tobytes(),
                          floatSize * self.vertexData.size)
        funcs.glEnableVertexAttribArray(0)
        nullptr = VoidPtr(0)
        funcs.glVertexAttribPointer(0,
                                    3,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    3 * floatSize,
                                    nullptr)
        self.vbo.release()
        self.program.release()
        vaoBinder = None

    def cleanUpGl(self):
        "Clean up everything"
        self.context.makeCurrent()
        self.vbo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()

    def resizeGL(self, width: int, height: int):
        "Resize the viewport"
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)

    def paintGL(self):
        "drawing loop"
        funcs = self.context.functions()

        # clean up what was drawn
        funcs.glClear(pygl.GL_COLOR_BUFFER_BIT)

        # actual drawing
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        funcs.glDrawArrays(pygl.GL_TRIANGLES,  # mode
                           0,  # first
                           3)  # count
        self.program.release()
        vaoBinder = None

def main():
    app = QApplication(sys.argv)
    window = TriangleGL()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
