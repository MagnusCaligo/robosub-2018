from Ui_Map.ui_mapWidget import Ui_MapWidget
from Ui_Map.mapWidget import MapWidget
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

class Map(QtCore.QObject):
    """
    Creates a map with a bunch of features such as running a
    simulation. Viewing the sub's current movements and 'thoughts'.
    """
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.UI_Map = MapWidget(externalComm)
        self._meshList = None           #Populate mesh list in here

        self.actualSub = None
        self.desiredSub = None

        self.verts = None
        self.faces = None
        self.colors = None

        self.yRotDeg = 0.0 # yaw
        self.xRotDeg = 0.0 # pitch
        self.zRotDeg = 0.0 # roll
        self.yTrans = -2.0
        self.xTrans = -2.0
        self.zTrans = -2.0

        self.externalComm = externalComm

        self.timer = QtCore.QTimer()
        self.timer.start(200)

        self._startSim = False

    def connectSignals(self):
        """
        Connect the signals.

        :return:
        """
        self.connect(self.externalComm, QtCore.SIGNAL("ExternalCommThreadFinished()"), self.update)
        #self.ui_map.startSimButton.clicked.connect(lambda: self.startSimulation())
        self.timer.timeout.connect(self.update)


    def update(self):
        if self.externalComm.guiDataToSend["missionList"] is not None:
            for i in range(0, len(self.externalComm.guiDataToSend["missionList"])):
                if not self.externalComm.guiDataToSend["missionList"][i].generalWaypoint:
                    self.externalComm.guiDataToSend["missionList"][i].generalWaypoint = [0, 0, 0]
                self.UI_Map.setWaypoint(self.externalComm.guiDataToSend["missionList"][i])

    def createFollowLine(self):
        pos = np.vstack([self.xTrans, self.yTrans, self.zTrans]).transpose()
        line = gl.GLLinePlotItem(pos=pos, color=pg.glColor((4,20*1.3)), width=(20+1)/10.,
                                                           antialias=True)

