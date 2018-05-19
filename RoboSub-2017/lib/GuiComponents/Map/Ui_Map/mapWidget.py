from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from SceneObject import SceneObject
from SceneObject import MeshUtil
from SceneObject import Vec3
from SceneObject import Manipulator
from lib.Utils.SlideEdit import SlideEdit
import os

class MechaGLWidget(gl.GLViewWidget):
    manipulatorMode = QtCore.pyqtSignal()
    NorthCoordChanged = QtCore.pyqtSignal(object)             #X - Axis
    EastCoordChanged = QtCore.pyqtSignal(object)              #Y - Axis
    UpCoordChanged = QtCore.pyqtSignal(object)                #Z - Axis
    YawOrientChanged = QtCore.pyqtSignal(object)
    PitchOrientChanged = QtCore.pyqtSignal(object)
    RollOrientChanged = QtCore.pyqtSignal(object)
    def __init__(self, externalComm):
        self.waypointList = {}
        self.externalComm = externalComm
        self.sphereMesh = MeshUtil.LoadMesh("lib/GuiComponents/Map/SceneUtil/Mesh/sphere.obj")
        super(MechaGLWidget, self).__init__()
        self.isMouseDown = False
        self.isInManipulatorMode = False
        self.activeWaypoint = ""
        self.lastActiveWaypoint = ""

    def setActiveWayPoint(self, activeInd):
        """
        Sets Current Waypoint to desired. 
        :param activeInd: 
        :return: 
        """
        if activeInd in self.waypointList.keys():
            # if self.activeWaypoint != "":
            #     self.waypointList[self.activeWaypoint].object.faceColors = [1, 1, 0, 1]
            self.activeWaypoint = str(activeInd)
            #self.waypointList[self.activeWaypoint].object.faceColors = [1, 0, 1, 1]
            self.NorthCoordChanged.emit(self.waypointList[self.activeWaypoint].transform.translate.vals[0])
            self.EastCoordChanged.emit(self.waypointList[self.activeWaypoint].transform.translate.vals[1])
            self.UpCoordChanged.emit(self.waypointList[self.activeWaypoint].transform.translate.vals[2])
            self.YawOrientChanged.emit(self.waypointList[self.activeWaypoint].transform.rotate.vals[0])
            self.PitchOrientChanged.emit(self.waypointList[self.activeWaypoint].transform.rotate.vals[1])
            self.RollOrientChanged.emit(self.waypointList[self.activeWaypoint].transform.rotate.vals[2])
        else:
            self.activeWaypoint = ""

    def setWaypoint(self, waypointInfo):
        """
        Adds waypoint if waypoint is not present.
        :param waypointInfo: 
        :return: 
        """
        if not waypointInfo.name in self.waypointList.keys():
            pos = Vec3(waypointInfo.generalWaypoint[0], waypointInfo.generalWaypoint[1], waypointInfo.generalWaypoint[2] )
            orientation = Vec3(waypointInfo.generalWaypoint[3], waypointInfo.generalWaypoint[4], waypointInfo.generalWaypoint[5])
            #orientation = Vec3(0, 0, 0)
            mesh = self.sphereMesh
            col = []
            if waypointInfo.reachedGeneralWaypoint is True:
                col = [1, 0, 0, 1]
            else:
                col = [1, 1, 0, 1]
            self.waypointList[waypointInfo.name] = SceneObject(pos, mesh[0], mesh[1], mesh[2], col, 1)
            self.waypointList[waypointInfo.name].setOrientation(orientation)
            self.addItem(self.waypointList[waypointInfo.name].object)

    def removeWaypoint(self, waypointInfo):
        #TODO Implement remove Waypoint from Map if something occurred.
        pass

    def adjustActiveWaypoint_transX(self, value):
        """
        Sets new X(North) Value for Translation 
        :param value: New Value
        :return: 
        """
        if self.activeWaypoint is not "":
            trans = self.waypointList[self.activeWaypoint].transform.translate.vals[0]
            self.waypointList[self.activeWaypoint].object.translate(-trans, 0.0, 0.0)
            self.waypointList[self.activeWaypoint].transform.translate.vals[0] = value
            self.waypointList[self.activeWaypoint].object.translate(value, 0.0, 0.0)
            self.externalComm.setWaypointX(self.activeWaypoint, value)

    def adjustActiveWaypoint_transY(self, value):
        if self.activeWaypoint is not "":
            trans = self.waypointList[self.activeWaypoint].transform.translate.vals[1]
            self.waypointList[self.activeWaypoint].object.translate(-0.0, -trans, 0.0)
            self.waypointList[self.activeWaypoint].transform.translate.vals[1] = value
            self.waypointList[self.activeWaypoint].object.translate(0.0, value, 0.0)
            self.externalComm.setWaypointY(self.activeWaypoint, value)

    def adjustActiveWaypoint_transZ(self, value):
        if self.activeWaypoint is not "":
            trans = self.waypointList[self.activeWaypoint].transform.translate.vals[2]
            self.waypointList[self.activeWaypoint].object.translate(0.0, 0.0, trans)
            self.waypointList[self.activeWaypoint].transform.translate.vals[2] = value
            self.waypointList[self.activeWaypoint].object.translate(0.0, 0.0, -value)
            self.externalComm.setWaypointZ(self.activeWaypoint, value)

    #Yaw, Pitch, and Roll here do NOT match with the actual axis, it should be yaw = y, pitch = x, roll = z
    #They aren't in the right order because they are in x,y,z order on the map widget
    def adjustActiveWaypoint_orientX(self, value):
        if self.activeWaypoint is not "":
            self.externalComm.setWaypointOrientation_Yaw(self.activeWaypoint, value)
            print value

    def adjustActiveWaypoint_orientY(self, value):
        if self.activeWaypoint is not "":
            self.externalComm.setWaypointOrientation_Pitch(self.activeWaypoint, value-180)

    def adjustActiveWaypoint_orientZ(self, value):
        if self.activeWaypoint is not "":
            self.externalComm.setWaypointOrientation_Roll(self.activeWaypoint, value-180)

    # @Override
    def mousePressEvent(self, QMouseEvent):
        super(MechaGLWidget, self).mousePressEvent(QMouseEvent)
        if QMouseEvent.button() == 1:
            self.isMouseDown = True

    # @Override
    def mouseMoveEvent(self, QMouseEvent):
        if not self.isInManipulatorMode:
            super(MechaGLWidget, self).mouseMoveEvent(QMouseEvent)
        else:
            print "Doing Manipulator stuff. "
    #@Override
    def mouseReleaseEvent(self, QMouseEvent):
        super(MechaGLWidget, self).mouseReleaseEvent(QMouseEvent)
        if self.isMouseDown is True:
            self.isMouseDown = False


class MapWidget(QtGui.QWidget):
    def __init__(self, externalComm):
        super(MapWidget, self).__init__()
        self.externalComm = externalComm
        self.waypointList = []
        self.sphereMesh = MeshUtil.LoadMesh("lib/GuiComponents/Map/SceneUtil/Mesh/sphere.obj")
        self.manipXMesh = MeshUtil.LoadMesh("lib/GuiComponents/Map/SceneUtil/Mesh/manipX.obj")
        self.manipYMesh = MeshUtil.LoadMesh("lib/GuiComponents/Map/SceneUtil/Mesh/manipY.obj")
        self.manipZMesh = MeshUtil.LoadMesh("lib/GuiComponents/Map/SceneUtil/Mesh/manipZ.obj")
        self.manipulatorTool = Manipulator(self.manipXMesh, self.manipYMesh, self.manipZMesh)

    def addWaypoint(self, pos, passed):
        """
        Adds a new Waypoint to the Waypoint Map
        :param pos: Position of waypoint.
        :param passed: Flag of whether Waypoint was passed or not. 
        :return: 
        """
        mesh = self.sphereMesh
        self.waypointList.append(SceneObject(pos, mesh[0], mesh[1],mesh[2], [1, 0, 0, 1], 1))

    def setWaypoint(self, waypointInfo):
        if self.itmComboBox.findText(waypointInfo.name) is -1:
            self.itmComboBox.addItem(waypointInfo.name)
        self._viewportWidget.setWaypoint(waypointInfo)

    def addItem(self):
        """
        Adds Arbitrary items to 3dMap Viewport
        :return: 
        """
        arr = self.sphereMesh
        sceneObject = SceneObject(Vec3(0, 0, 0), arr[0], arr[1],arr[2], [0, 0, 1, 1])
        self._viewportWidget.addItem(sceneObject.object)

    def removeItem(self, name):
        if self.itmComboBox.findText(name) > 0:
            self.itmComboBox.removeItem(name)


    def clearItems(self):
        print "Clears all Items in scene. "

    def initGUI(self, parent):
        """
        Initializes the GUI
        :param parent: Parent Pointer
        :return: 
        """
        # -- Begin Viewport Widget
        self._viewportWidget = MechaGLWidget(self.externalComm)
        self._viewportWidget.setMinimumWidth(800)
        self._viewportWidget.setCameraPosition(distance=50)
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        grid.setDepthValue(10)
        self._viewportWidget.addItem(grid)
        self._viewportWidget.setMinimumHeight(600)
        self._playPauseBtn = QtGui.QPushButton("Play", self)
        viewportLayout = QtGui.QVBoxLayout()
        viewportLayout.addWidget(self._viewportWidget)
        viewportLayout.addWidget(self._playPauseBtn)

        itmLbl = QtGui.QLabel("Item", self)
        self.itmComboBox = QtGui.QComboBox(self)
        self.itmComboBox.addItem("None")

        viewWidget = QtGui.QWidget()
        viewWidget.setLayout(viewportLayout)

        xLbl = QtGui.QLabel("North", self)
        yLbl = QtGui.QLabel("East", self)
        zLbl = QtGui.QLabel("Up", self)
        translateLbl = QtGui.QLabel("Translate", self)
        rotateLbl = QtGui.QLabel("Rotate", self)

        self.transXLE = QtGui.QSpinBox(self)
        self.transXLE.setMinimum(-1000)
        self.transYLE = QtGui.QSpinBox(self)
        self.transYLE.setMinimum(-1000)
        self.transZLE = QtGui.QSpinBox(self)
        self.transZLE.setMinimum(-1000)

        self.rotXLE = SlideEdit()
        self.rotXLE.updateMin(0)
        self.rotXLE.updateMax(360)
        self.rotXLE.setCurrentValue(360)
        self.rotXLE.setEnabled(True)
        self.rotXLE._lockBounds = True

        self.rotYLE = SlideEdit()
        self.rotYLE.updateMin(0)
        self.rotYLE.updateMax(360)
        self.rotYLE.setCurrentValue(360)
        self.rotYLE.setEnabled(True)
        self.rotYLE._lockBounds = True

        self.rotZLE = SlideEdit()
        self.rotZLE.updateMin(0)
        self.rotZLE.updateMax(360)
        self.rotZLE.setCurrentValue(360)
        self.rotZLE.setEnabled(True)
        self.rotZLE._lockBounds = True

        transformGridLayout = QtGui.QGridLayout()
        transformGridLayout.addWidget(itmLbl, 0, 0)
        transformGridLayout.addWidget(self.itmComboBox, 0, 1, 1, 3)
        transformGridLayout.addWidget(xLbl, 1, 1)
        transformGridLayout.addWidget(yLbl, 1, 3)
        transformGridLayout.addWidget(zLbl, 1, 5)

        transformGridLayout.addWidget(translateLbl,  2, 0)
        transformGridLayout.addWidget(self.transXLE, 2, 1)
        transformGridLayout.addWidget(self.transYLE, 2, 3)
        transformGridLayout.addWidget(self.transZLE, 2, 5)
        transformGridLayout.addWidget(rotateLbl, 3, 0)
        transformGridLayout.addWidget(self.rotXLE, 3, 1)
        transformGridLayout.addWidget(self.rotYLE, 3, 3)
        transformGridLayout.addWidget(self.rotZLE, 3, 5)

        # -- Begin Settings Widget
        self.dispWaypointsCB = QtGui.QCheckBox("Display Waypoints", self)
        self.dispDesiredPosition = QtGui.QCheckBox("Display Desired Position", self)
        self.dispVoxelCB = QtGui.QCheckBox("Display Voxel Data", self)

        sceneLbl = QtGui.QLabel("Scene: ", self)

        self.sceneOptions = QtGui.QComboBox(self)
        self.sceneOptions.addItem("Aquaplex")
        self.sceneOptions.addItem("Transdec1")
        self.sceneOptions.addItem("Transdec2")
        self.sceneOptions.addItem("Transdec3")
        self.sceneOptions.addItem("Transdec4")

        voxelResLbl = QtGui.QLabel("Voxel Resolution: ", self)
        self._voxelResSB = QtGui.QSpinBox(self)

        viewLayout = QtGui.QGridLayout()
        viewLayout.addWidget(self.dispWaypointsCB, 0, 0)
        viewLayout.addWidget(self.dispDesiredPosition, 1, 0)
        viewLayout.addWidget(self.dispVoxelCB, 2, 0)
        viewLayout.addWidget(sceneLbl, 3, 0)
        viewLayout.addWidget(self.sceneOptions, 3, 1)
        viewLayout.addWidget(voxelResLbl, 4, 0)
        viewLayout.addWidget(self._voxelResSB, 4, 1)

        loadSimulationBtn = QtGui.QPushButton("Load Simulation", self)
        loadVoxelData = QtGui.QPushButton("Load Voxel Data", self)
        loadLayout = QtGui.QGridLayout()
        loadLayout.addWidget(loadSimulationBtn, 0, 0)
        loadLayout.addWidget(loadVoxelData, 0, 1)

        transformGrpBox = QtGui.QGroupBox()
        transformGrpBox.setTitle("Transform")
        transformGrpBox.setLayout(transformGridLayout)

        viewGrpBox = QtGui.QGroupBox()
        viewGrpBox.setTitle("View")
        viewGrpBox.setLayout(viewLayout)

        loadOptionsBox = QtGui.QGroupBox()
        loadOptionsBox.setTitle("Load Files")
        loadOptionsBox.setLayout(loadLayout)

        settingsLayout = QtGui.QVBoxLayout()
        settingsLayout.addWidget(transformGrpBox)
        settingsLayout.addWidget(viewGrpBox)
        settingsLayout.addWidget(loadOptionsBox)
        settingsLayout.addSpacerItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        settingsWidget = QtGui.QWidget(self)
        settingsWidget.setLayout(settingsLayout)
        settingsWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        splitArea = QtGui.QSplitter(self)
        splitArea.addWidget(viewWidget)
        splitArea.addWidget(settingsWidget)

        centralLayout = QtGui.QVBoxLayout()
        centralLayout.addWidget(splitArea)
        parent.setLayout(centralLayout)
        for i in range(0, 3):
            self._viewportWidget.addItem(self.manipulatorTool.meshList[i].object)

        self.manipulatorTool.setVisible(False)
        self.connectSignals()

    def connectSignals(self):
        self.itmComboBox.currentIndexChanged.connect(self.adjustText)
        self.transXLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_transX)
        self.transYLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_transY)
        self.transZLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_transZ)
        self.rotXLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_orientX)
        self.rotYLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_orientY)
        self.rotZLE.valueChanged.connect(self._viewportWidget.adjustActiveWaypoint_orientZ )
        self._viewportWidget.NorthCoordChanged.connect(self.setTranslateXValue)
        self._viewportWidget.EastCoordChanged.connect(self.setTranslateYValue)
        self._viewportWidget.UpCoordChanged.connect(self.setTranslateZValue)
        self._viewportWidget.YawOrientChanged.connect(self.setYawValue)
        self._viewportWidget.PitchOrientChanged.connect(self.setPitchValue)
        self._viewportWidget.RollOrientChanged.connect(self.setRollValue)

    def setTranslateXValue(self, value):
        self.transXLE.setValue(value)

    def setTranslateYValue(self, value):
        self.transYLE.setValue(value)

    def setTranslateZValue(self, value):
        self.transZLE.setValue(value)

    def setYawValue(self, value):
        self.rotXLE.setCurrentValue(value)

    def setPitchValue(self, value):
        self.rotYLE.setCurrentValue(value + 180)

    def setRollValue(self, value):
        self.rotZLE.setCurrentValue(value + 180)

    def adjustText(self, changedIndex):
        inputStr = self.itmComboBox.itemText(changedIndex)
        if inputStr == "None":
            self.transXLE.setEnabled(False)
            self.transYLE.setEnabled(False)
            self.transZLE.setEnabled(False)
        else:
            self.transXLE.setEnabled(True)
            self.transYLE.setEnabled(True)
            self.transZLE.setEnabled(True)
        self._viewportWidget.setActiveWayPoint(inputStr)
