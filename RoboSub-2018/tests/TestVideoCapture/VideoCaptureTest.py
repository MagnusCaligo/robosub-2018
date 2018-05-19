import sys
import cv2
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QImage
import time
import graphic_overlay as graphOver
import numpy as np


class VideoCapture(QtGui.QWidget):
    def __init__(self, parent=None):
        super(VideoCapture, self).__init__()
        self.camera = None
        self.camera = cv2.VideoCapture(0)
        b, self.frame = self.camera.read()
        self.label = QtGui.QLabel()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.update)
        self.timer.start(100)
        #window = type("Foo", (object,), {})()
        #window.DEBUG = True
        #window.width = 640
        #window.height = 480
        self.HUD = graphOver.GraphicOverlay(window, window.width, window.height)
        self.RGB = [19, 242, 45]
        #dino = cv2.imread("cute dinosaur.png", cv2.IMREAD_COLOR)
        #self.right = dino[0:480, 0:640]
        #self.left = cv2.cvtColor(self.right, cv2.COLOR_RGB2BGR)

    def update(self):
        succ, self.frame = self.camera.read()
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.left = self.frame
        self.right = self.frame
        # self.left = self.frame[0:480, 0:640]
        #self.right = self.frame[0:480, 640:1280]
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


class Main(QtGui.QMainWindow):
    def __init(self, parent=None):
        super(Main, self).__init__(parent)
        self.mainLayout = QtGui.QVBoxLayout()
        self.videoCapture = VideoCapture()
        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.videoCapture)


app = QtGui.QApplication(sys.argv)
myWidget = Main()
myWidget.show()

sys.exit(app.exec_())