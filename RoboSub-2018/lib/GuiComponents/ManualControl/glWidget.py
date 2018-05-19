from PyQt4 import QtGui
from PyQt4 import QtOpenGL
from OpenGL import GLU
from OpenGL.GL import *
from numpy import array

class GLWidget(QtOpenGL.QGLWidget):
    """
    Creates a 3D cube that can rotate based on
    angles sent over serial communication
    """
    def __init__(self, parent=None):
        """
        Initializes variables and starts the serial communication
        :param parent: window the GLWidget will be contained in
        """
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent=None)
        self.yRotDeg = 0.0 # yaw
        self.xRotDeg = 0.0 # pitch
        self.zRotDeg = 0.0 # roll
        self.yTrans = -2.0
        self.xTrans = -2.0
        self.zTrans = -2.0

    def initializeGL(self):
        """
        Initializes open GL
        :return:
        """
        self.qglClearColor(QtGui.QColor(0, 0, 0))
        self.Geometry()

        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        """
        Adds viewport and projection to fit the size
        of the screen
        :param width: Width of the screen
        :param height: Height of the screen
        :return:
        """
        if height == 0: height = 1

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        Gives the cube its rotation and translation.  Also
        paints the color onto the cube
        :return:
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslate(25, 30.0, -70.0)
        glScale(15.0, 15.0, 15.0)
        glRotate(-self.yRotDeg, 1.0, 0.0, 0.0)
        glRotate(-self.xRotDeg, 0.0, 1.0, 0.0)
        glRotate(-self.zRotDeg, 0.0, 0.0, 1.0)

        glTranslate(self.xTrans, self.yTrans, self.zTrans)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointerf(self.cubeVtxArray)
        glColorPointerf(self.cubeClrArray)
        glDrawElementsui(GL_QUADS, self.cubeIdxArray)

    def Geometry(self):
        """
        Builds the vertices of the cube.
        :return:
        """
        self.cubeVtxArray = array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0]])
        self.cubeIdxArray = [
                0, 1, 2, 3,
                3, 2, 6, 7,
                1, 0, 4, 5,
                2, 1, 5, 6,
                0, 3, 7, 4,
                7, 6, 5, 4 ]
        self.cubeClrArray = [
                [0.0, 1.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 0.6, 0.0],
                [1.0, 0.6, 0.0 ]]

    def spin(self):
        """
        Sets the cubes rotation based on the serial input
        :return:
        """
        self.yRotDeg += (5) % 360.0
        self.xRotDeg += (5) % 360.0
        self.zRotDeg += (5) % 360.0
        self.updateGL()

