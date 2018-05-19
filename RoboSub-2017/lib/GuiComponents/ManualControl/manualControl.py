from PyQt4 import QtCore
from PyQt4 import QtGui
from glWidget import GLWidget
from Ui_ManualControl.ui_manualControlWidget import Ui_ManualControlWidget
import time

class ManualControl(QtCore.QObject):
    """
    Sets up the ui for the ManualControl widget.
    """
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.ui_manualControl = Ui_ManualControlWidget()
        self.worker = None
        self.worker_thread = None
        self.startPressed = False
        self.externalComm = externalComm
        
    def connectSignals(self):
        self.ui_manualControl.startButton.clicked.connect(self.startButtonPressed)

    def setWidget(self, widget):
        """
        Sets cube widget to widget passed and connects the button events.
        :param widget: QWidget from mainWindow manualControlWidget
        :return: None
        """
        self.cubeWidget = GLWidget(widget)
        #self.worker_thread = WorkerThread(self.cubeWidget)
        self.ui_manualControl.startButton.clicked.connect(lambda: self.startButtonPressed())
        self.connect(self.worker_thread, QtCore.SIGNAL("finished(QString)"), self.threadFinished)

    @QtCore.pyqtSlot()
    def threadFinished(self, outputMessage):
        self.worker_thread.wait()
        self.ui_manualControl.controlOutput.appendPlainText(outputMessage)
        self.worker_thread.start()

    @QtCore.pyqtSlot()
    def startButtonPressed(self):
        """
        Starts manual control.
        :return:  None
        """
        if not self.startPressed:
            """
            Start button isn't pressed so start thread.
            """
            #self.worker_thread.start()
            if self.externalComm.isDebug == False:
                self.ui_manualControl.startButton.setText("Stop")
                self.startPressed = True
                self.externalComm.missionPlanner.startManualControl()
                self.externalComm.externalCommThread.isDebug = False
                self.externalComm.running = True
                self.externalComm.externalCommThread.isRunning = True
                self.externalComm.externalCommThread.isDebug = False
                self.externalComm.externalCommThread.start()

        elif self.startPressed:
            """
            Start button is pressed again which means the user
            is trying to stop thread.
            """
            #self.worker_thread.stop()
            self.startPressed = False
            self.ui_manualControl.startButton.setText("Start")
            self.externalComm.missionPlanner.stopManualControl()
'''
class WorkerThread(QtCore.QThread):
    """
    Worker thread specific to the manual control widget.
    Reads in positional data and updates the gl Cube widget
    based on that positional data.
    """
    finished = QtCore.pyqtSignal(object)
    def __init__(self, glWidget):
        """
        :param widget: GlWidget class
        """
        QtCore.QThread.__init__(self)
        self.glWidget = glWidget
        self.yaw= 0.0 # yaw
        self.pitch = 0.0 # pitch
        self.roll = 0.0 # roll
        self.yTrans = -2.0
        self.xTrans = -2.0
        self.zTrans = -2.0
        self.position = " "
        self.pause = False
        self._isRunning = True

    def stop(self):
        """
        Stops thread
        :return: None
        """
        self._isRunning = False

    def run(self):
        """
        Updates the position of the gl widget
        based on the position of the sub. Stops
        when self._isRunning = False
        :return: None
        """
        print ('%s, %s,' % (QtCore.QThread.currentThread(), int(QtCore.QThread.currentThreadId())))
        if self._isRunning:
            """
            Spin the 3D cube.  Get the 3D coordinates
            and write to the plain text box
            """
            time.sleep(0.01)
            self.glWidget.spin()
            self.yaw = self.glWidget.yRotDeg
            self.pitch = self.glWidget.xRotDeg
            self.roll = self.glWidget.zRotDeg
            self.yTrans = self.glWidget.yTrans
            self.xTrans = self.glWidget.xTrans
            self.zTrans = self.glWidget.zTrans
            self.position = "Yaw: " + str(self.yaw) + "Pitch: " + str(self.pitch) + "Roll: " + str(self.roll)
            self.position += "X: " + str(self.xTrans) + "Y: " + str(self.yTrans) + "Z: " + str(self.zTrans)
            #self.ui_manualControl.controlOutput.appendPlainText(self.position)
            time.sleep(0.01)
            self.emit(QtCore.SIGNAL("finished(QString)"), self.position)
        #elif not self._isRunning:
'''