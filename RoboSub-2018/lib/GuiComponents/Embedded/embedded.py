from PyQt4 import QtCore
from Ui_Embedded.ui_embeddedWidget import Ui_EmbeddedWidget
from lib.ExternalDevices.external_communication import ExternalComm
from lib.ExternalDevices.external_communication import ExternalCommThread



class EmbeddedWidget(QtCore.QObject):
    """
    Class that handles the embedded communication with the GUI and the external devices.
    """
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.ui_embedded = Ui_EmbeddedWidget()
        #self.externalCommThread = ExternalCommThread()
        self.externalComm = externalComm


    def connectSignals(self):
        self.ui_embedded.startButton.clicked.connect(lambda: self.startButtonPressed())

    @QtCore.pyqtSlot()
    def startButtonPressed(self):
        print ("Embedded Widget Start Button Pressed")
        self.connectSignals()

    def connectSignals(self):
        """
        Displays the external device output to the text box
        :return:
        """
        self.connect(self.externalComm, QtCore.SIGNAL("ExternalDataReady()"),
                     self.externalCommThreadFinished)
        #self.connect(self.externalCommThread, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.externalCommThreadFinished)
        print ("Connected")

    def externalCommThreadFinished(self):
        print ("Adding text")
        self.ui_embedded.plainTextEdit.appendPlainText(self.externalComm.ahrsData)