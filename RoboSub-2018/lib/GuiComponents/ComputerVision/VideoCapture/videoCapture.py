import cv2
import lib.Utils.graphic_overlay as graphOver
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import QImage


class VideoCapture(QtCore.QObject):
    
    startVideoCaptureThread = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QObject.__init__(self)
        #self.ui_computerVision = Ui_ComputerVisionWidget()
        self.gridLayout = QtGui.QGridLayout()
        self.videoCaptureThread = None
        self.obstacleLocations = None
        self.startPressed = False
        self.timer = QtCore.QTimer()
        self.camera = cv2.VideoCapture(0)    

    def update(self):
        if self.camera == None:
            return
        b, self.frame = self.camera.read()
        self.label = QtGui.QLabel()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.width = 640
        self.height = 480
        self.HUD = graphOver.GraphicOverlay(self, self.width, self.height)
        self.RGB = [19, 242, 45]
        succ, self.frame = self.camera.read()
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.left = self.frame[0:480, 0:640]
        self.right = self.frame[0:480, 640:1280]
        self.left = self.frame.copy()
        self.right = self.frame.copy()
        self.HUD.drawHeadingGauge(self.left, 10, 36, 1, 500, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawPitchGauge(self.left, 10, 36, 600, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawRollGauge(self.left, 10, 36, 0, 270, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawDepthGauge(self.left, 10, 36, 1, 410, self.RGB, [30, 30, [30, 30], 30, 30])
        self.HUD.drawAttitude(self.left, 40, 1, 0, 3, 3, self.RGB, [[270, 90, 30], [270, 90, 30], None, None, None],
                              [360, 180, 120], [10, 20, 30], [0, 12, 0])
        self.HUD.drawTemperature(self.left, 15, 3, self.RGB, 30)
        self.HUD.drawBatteryGauge(self.left, 80, 1, 1, self.RGB, [60, 60, 60, 60])
        self.HUD.drawMotorGauges(self.left, 40, 0, self.RGB, [50, 50, 50, 50, 50, 50, 50, 50], [1, 0, 1, 0, 1, 0, 1, 0])

        self.HUD.drawHeadingGauge(self.right, 10, 36, 1, 500, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawPitchGauge(self.right, 10, 36, 600, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawRollGauge(self.right, 10, 36, 0, 270, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawDepthGauge(self.right, 10, 36, 1, 410, self.RGB, [30, 30, [30, 30], 30, 30])
        self.HUD.drawAttitude(self.right, 40, 1, 0, 3, 3, self.RGB, [[270, 90, 30], [270, 90, 30], None, None, None],
                              [360, 180, 120], [10, 20, 30], [0, 12, 0])
        self.HUD.drawTemperature(self.right, 15, 3, self.RGB, 30)
        self.HUD.drawBatteryGauge(self.right, 80, 1, 1, self.RGB, [60, 60, 60, 60])
        self.HUD.drawMotorGauges(self.right, 40, 0, self.RGB, [50, 50, 50, 50, 50, 50, 50, 50],
                                 [1, 0, 1, 0, 1, 0, 1, 0])

        self.frame = np.hstack((self.left, self.right))
        height, width, channel = self.frame.shape
        bpl = 3 * width
        self.qImg = QImage(self.frame.data, width, height, bpl, QImage.Format_RGB888)
        pix = QtGui.QPixmap(self.qImg)
        self.label.setPixmap(pix)
        self.label.show()
    
    def connectSignals(selfself):
        pass
    
    @QtCore.pyqtSlot()
    def hideSettings(self):
        pass
    
    @QtCore.pyqtSlot()
    def threadFinished(self):
        pass
    
    def startThread(self):
        pass
    
class VideoCaptureThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.outputMessage = None
        self.obstacleLocation = None
        self._isRunning = True
        self.videoCaptureClass = VideoCapture()

    def __del__(self):
        self.wait()

    def stop(self):
        self._isRunning = False
    
    def run(self):
        if self._isRunning:
            threadMessage = str(QtCore.QThread.currentThread()) + str(QtCore.QThread.currentThreadId())
            self.outputMessage = threadMessage
            #print "Running thread"
        self.emit(QtCore.SIGNAL('finished(QString)'), self.outputMessage)
