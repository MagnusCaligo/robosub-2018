import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import math as math

class Transform():
    """
    Transform class for caching transformation values. 
    """
    def __init__(self):
        self.translate = None
        self.rotate = None
        self.scale = None

class Vec3():
    def __init__(self, x = None, y = None, z = None):
        self.vals = []
        self.vals.append(x)
        self.vals.append(y)
        self.vals.append(z)

    def negate(self):
        self.vals[0] = -self.vals[0]
        self.vals[1] = -self.vals[1]
        self.vals[2] = -self.vals[2]

class BoundingBox():
    def __init__(self, bounds):
        self.pts = bounds

    def updateBounds(self, newPos):

        self.pts[0] += newPos.vals[0]
        self.pts[1] += newPos.vals[0]
        self.pts[2] += newPos.vals[1]
        self.pts[3] += newPos.vals[1]
        self.pts[4] += newPos.vals[2]
        self.pts[5] += newPos.vals[2]

    def intersects(self, pt):
        return (pt.x > self.pts[0] and
            pt.x < self.pts[1] and
            pt.y > self.pts[2] and
            pt.y < self.pts[3] and
            pt.z > self.pts[4] and
            pt.z < self.pts[5])

class MeshUtil():
    @staticmethod
    def LoadMesh(fileName):
        verts = []
        faces = []
        bounds = [0, 0, 0, 0, 0, 0]
        f = open(fileName, 'r')
        for line in f:
            if line[0] is 'v':
                if line[1] is ' ':
                    extract = line[2:]
                    vertStr = extract.split(" ")
                    verts.append([float(vertStr[0]), float(vertStr[1]), float(vertStr[2])])
                    bounds[0] = min(bounds[0], float(vertStr[0]))
                    bounds[1] = max(bounds[0], float(vertStr[0]))
                    bounds[2] = min(bounds[1], float(vertStr[1]))
                    bounds[3] = max(bounds[1], float(vertStr[1]))
                    bounds[4] = min(bounds[2], float(vertStr[2]))
                    bounds[5] = max(bounds[2], float(vertStr[2]))
            if line[0] is 'f':
                extract = line[2:]
                faceSubStr = extract.split(" ")
                face = []
                for i in range(0, 3):
                   face.append(int(faceSubStr[i].split("/")[0]) - 1)
                faces.append(face)
        ret = []
        ret.append(verts)
        ret.append(faces)
        ret.append(bounds)
        return ret

class SceneObject():
    def __init__(self, position, vertList, faceList, bounds, color=None, type = 0):
        """
        Initializes a scene object.
        :param position: Position of the sceneObject(Expected to be Vector3)
        :param vertList: List of Verticies
        :param faceList: List of Faces
        :param bounds: Generated Bounds
        :param color: Color of Object
        :param type: 
        """
        col = []
        self.type = type
        self.bounds = BoundingBox(bounds)
        self.isSelected = False
        if color is not None:
            for i in range(0, np.array(vertList).size):
                col.append(color)
        self.object = gl.GLMeshItem(vertexes = np.array(vertList), faces=np.array(faceList), faceColors = col, smooth=True)
        self.transform = Transform()
        self.transform.translate = position
        self.bounds.updateBounds(self.transform.translate)
        self.object.translate(self.transform.translate.vals[0], self.transform.translate.vals[1], self.transform.translate.vals[2])

    def setTranslate(self, position):
        """
        Sets a new position and updates the bounds of the map
        :param position: New Translation position.
        :return: 
        """
        self.transform.translate = position
        self.bounds.updateBounds(self.transform.translate)
        self.object.translate(self.transform.translate.vals[0], self.transform.translate.vals[1], self.transform.translate.vals[2])

    def setOrientation(self, orientation):
        """
        Sets orientation of waypoint
        :param orientation: New Orienatation
        :return: 
        """
        self.transform.rotate = orientation


class Manipulator():
    def __init__(self, mesh1, mesh2, mesh3):
        self.transform = Transform()
        self.meshList = []
        self.meshList.append(SceneObject(Vec3(0, 0, 0), mesh1[0], mesh1[1], mesh1[2], [1, 0, 0, 1], 0))
        self.meshList.append(SceneObject(Vec3(0, 0, 0), mesh2[0], mesh2[1], mesh2[2], [0, 1, 0, 1], 0))
        self.meshList.append(SceneObject(Vec3(0, 0, 0), mesh3[0], mesh3[1], mesh3[2], [0, 0, 1, 1], 0))
        for i in range(0, 3):
            self.meshList[i].object.scale(0.45, 0.45, 0.45)

    def setVisible(self, boolean):
        for i in range(0, 3):
            self.meshList[i].object.setVisible(boolean)
