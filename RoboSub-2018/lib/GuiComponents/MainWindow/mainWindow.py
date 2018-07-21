from PyQt4 import QtGui
from PyQt4 import QtCore
from Ui_MainWindow.ui_mainWindow import Ui_MainWindow
from Ui_MainWindow.ui_mainWindowWidget import Ui_MainWindowWidget
from lib.ExternalDevices.previous_state_logging import Previous_State_Logging
import sys
import time

class MainWindow(QtGui.QMainWindow):
    """
    Creates the Main Window where the user can choose to open
    other windows or simply run the vehicle
    """
    def __init__(self, parent=None):
        """
        Loads the UI and widgets.
        :param parent: None
        """
        super(MainWindow, self).__init__(parent)

        self.ui_MainWindow = Ui_MainWindow()
        self.ui_MainWindow.setupUi(self)
        self.ui_MainWindow.mdiArea.tileSubWindows()
        self.setWindowTitle('RoboSub GUI 2017')
	
	self.startedAuto = False

        # Create widget instances
        self.mainWindowWidget = None
        self.subwindow = None
        self.mapWidget = None
        self.embeddedWidget = None
        self.computerVisionWidget = None
        self.manualControlWidget = None
        self.missionCommanderWidget = None
        self.dataGraphingWidget = None
        self.controlSystemWidget = None
        self.debugValuesWidget = None

        # Create classes instance
        self.manualControlClass = None
        self.mapClass = None
        self.embeddedClass = None
        self.computerVisionClass = None
        self.videoCaptureClass = None
        self.externalCommClass = None
        self.missionCommanderClass = None
        self.dataGraphingClass = None
        self.controlSystemClass = None
        self.debugValuesClass = None

        self.previousStateLogging = Previous_State_Logging('Previous_Save.csv')
        
        print ('%s, %s,' % (QtCore.QThread.currentThread(), int(QtCore.QThread.currentThreadId())))

        # Create external device lists
        self.startVehicle = False

        self.systemOutput = None


    def setClasses(self, classes):
        """
        Sets the classes
        :param classes: List of classes [ManualControl(), ComputerVision(), Map(), Embedded(), VideoCapture()]
        :return: None
        """
        self.manualControlClass = classes[0]
        self.computerVisionClass = classes[1]
        self.mapClass = classes[2]
        self.embeddedClass = classes[3]
        self.externalCommClass = classes[4]
        self.missionCommanderClass = classes[5]
        self.dataGraphingClass = classes[6]
        self.controlSystemClass = classes[7]
        self.debugValuesClass = classes[8]
        self.pneumaticsClass = classes[9]
        
        self.externalCommClass.connectSignals()
        filename = self.externalCommClass.previous_state_logging.getValue("previousWidgetConfig")
        if not filename == "0":
            #self.externalCommClass.widget_config_logging.loadConfigs(filename)
            pass
        else:
            print "Couldn't load file"

    def add_mainWidget(self):
        """
        Adds the mainWindowWidget to the Mdi area.
        :return: None
        """
        # Initialize widget
        self.mainWindowWidget = QtGui.QWidget()
        self.subwin_mainWidget = Ui_MainWindowWidget()
        self.subwin_mainWidget.setupUi(self.mainWindowWidget)

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.mainWindowWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.mainWindowWidget)
        self.subwindow.setWindowTitle('Main Window')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.mainWindowWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()
        threadMessage = str(QtCore.QThread.currentThread()) + str(QtCore.QThread.currentThreadId())
        self.ui_MainWindow.statusbar.showMessage(threadMessage)

        # Connect the button signals to slots
        self.subwin_mainWidget.mapButton.clicked.connect(lambda: self.add_mapWidget())
        self.subwin_mainWidget.embeddedButton.clicked.connect(lambda: self.add_embeddedWidget())
        self.subwin_mainWidget.computerVisionButton.clicked.connect(lambda: self.add_computerVisionWidget())
        self.subwin_mainWidget.manualControlButton.clicked.connect(lambda: self.add_manualControlWidget())
        self.subwin_mainWidget.missionCommanderButton.clicked.connect(lambda: self.add_missionCommanderWidget())
        self.subwin_mainWidget.dataGraphingButton.clicked.connect(lambda: self.add_dataGraphingWidget())
        self.subwin_mainWidget.controlSystemButton.clicked.connect(lambda: self.add_controlSystemWidget())
        self.subwin_mainWidget.debugValuesButton.clicked.connect(lambda: self.add_debugValuesWidget())
        self.subwin_mainWidget.startButton.clicked.connect(lambda: self.startPressed())
        self.subwin_mainWidget.stopButton.clicked.connect(lambda: self.stopPressed())
        self.subwin_mainWidget.saveConfigButton.clicked.connect(lambda: self.saveConfigValues())
        self.subwin_mainWidget.debugCheck.clicked.connect(lambda: self.changeText())
        self.subwin_mainWidget.loadConfigsButton.clicked.connect(lambda: self.loadConfigValues())
        self.subwin_mainWidget.loadMissionsButton.clicked.connect(lambda: self.loadMissions())
        self.subwin_mainWidget.resetButton.clicked.connect(self.resetButtonClicked)
        self.subwin_mainWidget.pneumaticsButton.clicked.connect(self.add_pneumaticsWidget)
        self.systemOutput = self.subwin_mainWidget.plainTextEdit;

        
        #Connect Data signal to update sensor info on Main Window Widget
        self.connect(self.externalCommClass.externalCommThread, QtCore.SIGNAL("Data Updated"), lambda: self.updateSensorDisplay())
		
        self.subwin_mainWidget.startButton.setText("Start Debug")
        self.subwin_mainWidget.stopButton.setText("Stop Debug")

    def resetButtonClicked(self):
        self.externalCommClass.resetPosition()
        self.subwin_mainWidget.plainTextEdit.clear()
		
    def updateSensorDisplay(self):
        self.subwin_mainWidget.northLabel.setText("North: " + str(self.externalCommClass.externalCommThread.position[0]))
        self.subwin_mainWidget.eastLabel.setText("East: " + str(self.externalCommClass.externalCommThread.position[1]))
        self.subwin_mainWidget.upLabel.setText("Up: " + str(self.externalCommClass.externalCommThread.position[2]))

        self.subwin_mainWidget.yawLabel.setText("Yaw: " + str(self.externalCommClass.externalCommThread.orientation[0]))
        self.subwin_mainWidget.pitchLabel.setText("Pitch: " + str(self.externalCommClass.externalCommThread.orientation[1]))
        self.subwin_mainWidget.rollLabel.setText("Roll: " + str(self.externalCommClass.externalCommThread.orientation[2]))

        self.subwin_mainWidget.batteryVoltageLabel.setText("Battery Voltage: " + str(self.externalCommClass.externalCommThread.batteryVoltage))
		
    @QtCore.pyqtSlot()
    def loadMissions(self):
        self.missionCommanderClass.openFileDialog()
        self.subwin_mainWidget.missionLoaded.setText(self.missionCommanderClass.missionName)

    @QtCore.pyqtSlot()
    def changeText(self):
        if self.subwin_mainWidget.debugCheck.isChecked():
            self.subwin_mainWidget.startButton.setText("Start Debug")
            self.subwin_mainWidget.stopButton.setText("Stop Debug")
            self.externalCommClass.changeDebug(True)
        else:
            self.subwin_mainWidget.startButton.setText("Start Vehicle")
            self.subwin_mainWidget.stopButton.setText("Stop Vehicle")
            self.externalCommClass.changeDebug(False)

    @QtCore.pyqtSlot()
    def saveConfigValues(self):
        #For each widget that is open, save position and size to a dictionary
        self.externalCommClass.widget_config_logging.saveConfigs()

    @QtCore.pyqtSlot()
    def loadConfigValues(self):
        self.externalCommClass.widget_config_logging.loadConfigs()


    def getGuiParams(self):
        """
        Retrieves all the necessary gui parameters and sends to the external comm class
        :return:
        """
        HSVMax = self.computerVisionClass.HSVMax

        ##
        ## MAKE SURE ANY KEYS THAT ARE GOING TO BE PASSED TO THE COMPUTER VISION PROCESS
        ## MATCH THE C++ CODE
        guiParams = {'hueMax': self.computerVisionClass.HSVMax[0], 'saturationMax': self.computerVisionClass.HSVMax[1],
                     'valueMax': self.computerVisionClass.HSVMax[2], 'hueMin': self.computerVisionClass.HSVMin[0],
                     'saturationMin': self.computerVisionClass.HSVMin[1], 'valueMin': self.computerVisionClass.HSVMin[2],
                     'cannyMin': self.computerVisionClass.cannyEdge[0], 'cannyMax': self.computerVisionClass.cannyEdge[1],
                     'minDisparity': self.computerVisionClass.stereoVision[0], 'maxDisparity': self.computerVisionClass.stereoVision[1],
                     'P1': self.computerVisionClass.stereoVision[2], 'P2': self.computerVisionClass.stereoVision[3],
                     'sad': self.computerVisionClass.stereoVision[4], 'ct_win_size': self.computerVisionClass.stereoVision[5],
                     'hc_win_size': self.computerVisionClass.stereoVision[6], 'bt_clip_value': self.computerVisionClass.stereoVision[7],
                     'max_diff': self.computerVisionClass.stereoVision[8], 'uniqueness_ratio': self.computerVisionClass.stereoVision[9],
                     'scan_lines_mask': self.computerVisionClass.stereoVision[10], 'useNN': self.computerVisionClass.useNN,
                     'useImage': self.computerVisionClass.useImage, 'useVideo': self.computerVisionClass.useVideo,
                     'nnPath': self.computerVisionClass.nnPath, 'imagePath': self.computerVisionClass.imagePath,
                     'videoPath': self.computerVisionClass.videoPath}
        return guiParams

    def getCVParams(self):
        """
        Retrieves all the necessary gui parameters and sends to the external comm class
        :return:
        """
        ##
        ## MAKE SURE ANY KEYS THAT ARE GOING TO BE PASSED TO THE COMPUTER VISION PROCESS
        ## MATCH THE C++ CODE
        cvParams = {'hueMax': self.computerVisionClass.HSVMax[0], 'saturationMax': self.computerVisionClass.HSVMax[1],
                     'valueMax': self.computerVisionClass.HSVMax[2], 'hueMin': self.computerVisionClass.HSVMin[0],
                     'saturationMin': self.computerVisionClass.HSVMin[1], 'valueMin': self.computerVisionClass.HSVMin[2],
                     'cannyMin': self.computerVisionClass.cannyEdge[0], 'cannyMax': self.computerVisionClass.cannyEdge[1],
                     'minDisparity': self.computerVisionClass.stereoVision[0], 'maxDisparity': self.computerVisionClass.stereoVision[1],
                     'P1': self.computerVisionClass.stereoVision[2], 'P2': self.computerVisionClass.stereoVision[3],
                     'sad': self.computerVisionClass.stereoVision[4], 'ct_win_size': self.computerVisionClass.stereoVision[5],
                     'hc_win_size': self.computerVisionClass.stereoVision[6], 'bt_clip_value': self.computerVisionClass.stereoVision[7],
                     'max_diff': self.computerVisionClass.stereoVision[8], 'uniqueness_ratio': self.computerVisionClass.stereoVision[9],
                     'scan_lines_mask': self.computerVisionClass.stereoVision[10], 'useNN': self.computerVisionClass.useNN,
                     'useImage': self.computerVisionClass.useImage, 'useVideo': self.computerVisionClass.useVideo,
                     'nnPath': self.computerVisionClass.nnPath, 'imagePath': self.computerVisionClass.imagePath,
                     'videoPath': self.computerVisionClass.videoPath}
        return cvParams

    @QtCore.pyqtSlot()
    def exitHandler(self):
        """
        Function that will handle cleaning closing the GUI and turning off the processes.
        :return:
        """
        self.externalCommClass.externalCommThread.cleanStop()
        #self.computerVisionClass.computerVisionThread.cleanStop()


    @QtCore.pyqtSlot()
    def startPressed(self):
        """
        If debug is checked then start debug mode else run the sub.
        :return:
        """
	if self.externalCommClass.running == True:
		self.stopPressed()
		time.sleep(1)
		if self.startedAuto == True:
			return
		self.startedAuto = True
	self.resetButtonClicked()
        if self.subwin_mainWidget.debugCheck.isChecked():
            self.externalCommClass.externalCommThread.isDebug = False
	    self.externalCommClass.isDebug = False
            self.systemOutput.insertPlainText("Starting Debug Mode\n")
            self.externalCommClass.running = True
            self.externalCommClass.externalCommThread.guiData = self.externalCommClass.guiDataToSend
            self.externalCommClass.externalCommThread.isRunning = True
            self.externalCommClass.externalCommThread.start()
            #self.externalCommClass.missionPlanner.startAutonomousRun(True)
            if self.externalCommClass.externalCommThread.dvlResponseThread != None:
				pass#self.externalCommClass.externalCommThread.dvlResponseThread.clearDistanceTraveled()
        else:
            time.sleep(5)
            print "Starting"
            self.systemOutput.insertPlainText("Starting Vehicle\n")
            if self.externalCommClass.externalCommThread.dvlResponseThread != None:
                self.externalCommClass.externalCommThread.dvlResponseThread.clearDistanceTraveled()
            
            startTime = time.time()
            #while (time.time()-startTime) < 10:
				#pass
            self.startVehicle = True
            self.externalCommClass.externalCommThread.isDebug = False
            #self.systemOutput.insertPlainText("Starting vehicle\n")
            self.externalCommClass.running = True
            self.externalCommClass.externalCommThread.guiData = self.externalCommClass.guiDataToSend
            self.externalCommClass.externalCommThread.isRunning = True
            self.externalCommClass.externalCommThread.start()
            self.externalCommClass.missionPlanner.startAutonomousRun(False)
            #if self.externalCommClass.externalCommThread.dvlResponseThread != None:
			#	self.externalCommClass.externalCommThread.dvlResponseThread.clearDistanceTraveled()
        #self.externalCommClass.missionPlanner.setMissionList(self.externalCommClass.guiDataToSend["missionList"])

    @QtCore.pyqtSlot()
    def stopPressed(self):
        """
        If debug is checked then stop debug mode else cleanly
        power down the sub.
        :return:
        """
        if self.subwin_mainWidget.debugCheck.isChecked():
            self.systemOutput.insertPlainText("Stopping Debug Mode\n")
        else:
            self.systemOutput.insertPlainText("Stopping Vehicle\n")
        self.startVehicle = False
        self.externalCommClass.running = False
        self.externalCommClass.stopThread()		
	
    @QtCore.pyqtSlot()
    def add_pneumaticsWidget(self):
        # Initialize widget
        self.pneumaticsWidget= QtGui.QWidget()
        self.pneumaticsClass.ui_Pneumatics.setupUi(self.pneumaticsWidget)
        self.pneumaticsClass.connectSignals()


        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.pneumaticsWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.pneumaticsWidget)
        self.subwindow.setWindowTitle('Pneumatics')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.pneumaticsWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()

    @QtCore.pyqtSlot()
    def add_debugValuesWidget(self):
        """
        Adds the mapWidget to the Mdi area
        :return: None
        """
        # Initialize widget
        self.debugValuesWidget= QtGui.QWidget()
        self.debugValuesClass.ui_DebugValues.setupUi(self.debugValuesWidget)
        self.debugValuesClass.connectSignals()


        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.debugValuesWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.debugValuesWidget)
        self.subwindow.setWindowTitle('Debug Values')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.debugValuesWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()

    @QtCore.pyqtSlot()
    def add_mapWidget(self):
        """
        Adds the mapWidget to the Mdi area
        :return: None
        """
        # Initialize widget
        self.mapWidget = QtGui.QWidget()
        self.mapClass.UI_Map.initGUI(self.mapWidget)
        self.mapClass.connectSignals()


        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.mapWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.mapWidget)
        self.subwindow.setWindowTitle('Map')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.mapWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()
        
        
    @QtCore.pyqtSlot()
    def add_controlSystemWidget(self):
        """
        Adds the mapWidget to the Mdi area
        :return: None
        """
        # Initialize widget
        self.controlSystemWidget = QtGui.QWidget()
        self.controlSystemClass.ui_controlSystemWidget.setupUi(self.controlSystemWidget)
        self.controlSystemClass.connectSignals()


        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.controlSystemWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.controlSystemWidget)
        self.subwindow.setWindowTitle('Control Systems')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.controlSystemWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()
        

    @QtCore.pyqtSlot()
    def add_computerVisionWidget(self):
        """
        Adds the computerVisionWidget to the Mdi area
        :return: None
        """
        # Initialize widget

        self.computerVisionWidget = QtGui.QWidget()
        self.computerVisionClass.ui_computerVision.setupUi(self.computerVisionWidget)

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.computerVisionWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.computerVisionWidget)
        self.computerVisionWidget.closeEvent = lambda event: self.computerVisionClass.closeThread()
        #self.computerVisionWidget.closeEvent = lambda event: sys.stdout.write(str("Blah") + "\n")
        self.subwindow.setWindowTitle('Computer Vision')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.computerVisionWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()

        #self.computerVisionClass.setWidget(self.computerVisionWidget)
        #self.computerVisionClass.ui_computerVision.verticalLayout_2.addWidget(self.computerVisionClass.videoCaptureWidget)
        self.computerVisionClass.connectSignals()
        self.computerVisionClass.startThread()

    @QtCore.pyqtSlot()
    def add_embeddedWidget(self):
        """
        Adds the embeddedWidget to the Mdi area
        :return:
        """
        # Initialize widget
        self.embeddedWidget = QtGui.QWidget()
        self.embeddedClass.ui_embedded.setupUi(self.embeddedWidget)
        self.embeddedClass.connectSignals()

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.embeddedWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.embeddedWidget)
        self.subwindow.setWindowTitle('Embedded Systems')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.embeddedWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()

    @QtCore.pyqtSlot()
    def add_manualControlWidget(self):
        """
        Adds the manualControlWidget to the Mdi area
        :return:
        """
        # Initialize widget
        self.manualControlWidget = QtGui.QWidget()
        self.manualControlClass.ui_manualControl.setupUi(self.manualControlWidget)

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.manualControlWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.manualControlWidget)
        self.subwindow.setWindowTitle('Manual Control')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.manualControlWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()
        self.manualControlClass.connectSignals()

        #self.manualControlClass.setWidget(self.manualControlWidget)
        #self.manualControlClass.ui_manualControl.verticalLayout.addWidget(self.manualControlClass.cubeWidget)

    @QtCore.pyqtSlot()
    def add_missionCommanderWidget(self):
        """
        Adds the manualControlWidget to the Mdi area
        :return:
        """
        print ("Adding mission commander widget")
        # Initialize widget
        self.missionCommanderWidget = QtGui.QWidget()
        self.missionCommanderClass.ui_missionCommander.setupUi(self.missionCommanderWidget)

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.missionCommanderWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.missionCommanderWidget)
        self.subwindow.setWindowTitle('Mission Commander')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.missionCommanderWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()

        self.missionCommanderClass.connectSignals()


    @QtCore.pyqtSlot()
    def add_dataGraphingWidget(self):
        """
        Adds the dataGraphingWidget to the Mdi area
        :return:
        """
        print ("Adding data graphing widget")
        # Initialize widget
        self.dataGraphingWidget= QtGui.QWidget()
        self.dataGraphingClass.ui_dataGraphing.setupUi(self.dataGraphingWidget)
        self.dataGraphingClass.connectSignals()
        #self.dataGraphingClass.setupGraph()

        # Initialize subwindow
        self.subwindow = QtGui.QMdiSubWindow(self.ui_MainWindow.mdiArea)
        self.dataGraphingWidget.setParent(self.subwindow)
        self.subwindow.setWidget(self.dataGraphingWidget)
        self.subwindow.setWindowTitle('Data Graphing')

        # Show new subwindow
        self.ui_MainWindow.mdiArea.addSubWindow(self.subwindow)
        self.dataGraphingWidget.show()
        self.subwindow.show()
        self.subwindow.widget().show()




