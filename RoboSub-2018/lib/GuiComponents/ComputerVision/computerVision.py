from PyQt4 import QtCore
from PyQt4 import QtGui
from Ui_ComputerVision.ui_computerVisionWidget import Ui_ComputerVisionWidget
import lib.Utils.graphic_overlay as graphOver
from lib.Utils.SlideEdit import SlideEdit
from PyQt4.QtGui import QImage
import cv2
import platform
import numpy as np
import subprocess
#import flycapture2 as fc2
import os
import os.path


class ComputerVision(QtCore.QObject):

    startComputerVisionThread = QtCore.pyqtSignal()
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.ui_computerVision = Ui_ComputerVisionWidget()
        self.gridLayout = QtGui.QGridLayout()
        self.computerVisionThread = None
        self.obstacleLocations = None
        self.layoutList = None
        self.labelList = None
        self.startPressed = False
        self.externalComm = externalComm
        self.HSVMax = [180,255,255]
        self.HSVMin = [0,0,0]
        self.cannyEdge = [0,0]
        self.stereoVision = [0,0,0,0,0,0,0,0,0,0,0]
        self.showSettings = True
        self.useNN = False
        self.useImage = True
        self.useVideo = False
        self.cameraCheck = False
        self.nnPath = " "
        self.imagePath = "processed.jpeg"
        self.videoPath = " "
        self.slideEdits = []

        self.os = platform.platform()

    def connectSignals(self):
        self.computerVisionThread = ComputerVisionThread(self)
        self.connect(self.computerVisionThread, QtCore.SIGNAL("finished(QString)"), self.threadFinished)
        self.ui_computerVision.hideSettingsButton.clicked.connect(lambda: self.hideSettings())
        self.connect(self.computerVisionThread, QtCore.SIGNAL("sendingVideo(PyQt_PyObject)"), self.update)
        self.ui_computerVision.saveImageSettingsButton.clicked.connect(lambda: self.saveImageSettings())
        self.ui_computerVision.useImageButton.clicked.connect(lambda: self.startUsingSingleImage())
        self.ui_computerVision.useVideoButton.clicked.connect(lambda: self.startUsingVideo())
        self.ui_computerVision.missionList.currentIndexChanged.connect(lambda newIndex: self.loadImageSettings(newIndex))
        self.connect(self.computerVisionThread, QtCore.SIGNAL("debugThreadMessage(PyQt_PyObject)"), self.debugThreadMessage)
        self.ui_computerVision.findModelButton.clicked.connect(lambda: self.findModel())
        self.ui_computerVision.useNNCheckBox.stateChanged.connect(lambda x: self.useNNChecked(x))
        self.ui_computerVision.runImageButton.clicked.connect(lambda True: self.useImage)
        self.ui_computerVision.runVideoButton.clicked.connect(lambda True: self.useVideo)

        


        self.layoutList = [self.ui_computerVision.horizontalLayout_9, self.ui_computerVision.horizontalLayout_10,
                           self.ui_computerVision.horizontalLayout_4, self.ui_computerVision.horizontalLayout_13,
                           self.ui_computerVision.horizontalLayout_15, self.ui_computerVision.horizontalLayout_5,
                           self.ui_computerVision.horizontalLayout_6, self.ui_computerVision.horizontalLayout_7,
                           self.ui_computerVision.horizontalLayout_8]
        self.labelList = ["hueMax", "saturationMax", "valueMax", "hueMin", "saturationMin", "valueMin", "thresholdMin", "thresholdMax", "minDisparity",
                          "maxDisparity", "P1", "P2", "sad", "ctwinsize", "hcwinsize", "btclipvalue", "max_diff",
                          "uniquenessratio", "scanlinesmask"]



        self._setSlideEdits()
        self._setSavedValues()
        
        self.emit(QtCore.SIGNAL("sendingHSVValues(PyQt_PyObject)"), [self.HSVMax, self.HSVMin])

    @QtCore.pyqtSlot()
    def useNNChecked(self, state):
        if state == 2:  # Checked
            self.useNN = True
        else:
            self.useNN = False


    @QtCore.pyqtSlot()
    def findModel(self):
        """
        Opens up a file browser to file a neural network model.
        :return:
        """
        # load an image to use:
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        # Sets dialog to open at a particular directory
        print ("Opening file dialog.")
        fileName = QtGui.QFileDialog.getOpenFileName(fileWidget, 'Open File', '/')
        try:
            if platform == "win32":
                fileName = fileName.replace('/', '\\')
                print "using: " + fileName
            self.nnPath = fileName
            self.ui_computerVision.modelPathLineEdit.setText(fileName)
        except:
            print ("Image not found or not correct image format.")

    @QtCore.pyqtSlot()
    def saveImageSettings(self):
        """
        Loops through all the sliders and appends the mission name to the end and saves
        the new slider values.
        :return:
        """
        print ("Saving image settings")
        index = self.ui_computerVision.missionList.currentIndex()
        for slide_edit in self.slideEdits:
            slide_edit._assignedLabel = slide_edit._assignedLabel.split("_")[0] + "_" + str(self.ui_computerVision.missionList.itemText(index))
        self.saveValues()

    @QtCore.pyqtSlot()
    def loadImageSettings(self, newIndex):
        """
        Loads the slider image settings based on the mission selected from missionList.
        :return:
        """
        index = self.ui_computerVision.missionList.currentIndex()
        missionName = str(self.ui_computerVision.missionList.itemText(newIndex))
        dictionary = self.externalComm.previous_state_logging.dictionary
        for value, key in enumerate(dictionary):
                for slide_edit in self.slideEdits:
                    if key.split("_")[0] in slide_edit._assignedLabel:  # find the slide_edit with the same beginning
                        slide_edit._assignedLabel = key.split("_")[0] + missionName
                        slide_edit.setCurrentValue(float(value))
                        print (key.split("_")[0])
                        print (slide_edit._assignedLabel)

    def _setSavedValues(self):
        """
        Sets the sliders to the values saved in the globals GUI_VARIABLES dictionary
        :return:
        """
        #self.externalComm.previous_state_logging.loadFile()
        dictionary = self.externalComm.previous_state_logging.dictionary
        if dictionary:
            for slide_edit in self.slideEdits:
                try:
                    slide_edit.setCurrentValue(float(dictionary[slide_edit._assignedLabel]))
                    if "hueMax" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMaxValues)
                    elif "saturationMax" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMaxValues)
                    elif "valueMax" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMaxValues)
                    elif "hueMin" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMinValues)
                    elif "saturationMin" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMinValues)
                    elif "valueMin" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateMinValues)
                    elif "thresholdMin" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateCannyValues)
                    elif "thresholdMax" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateCannyValues)
                    elif "minDisparity" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "maxDisparity" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "P1" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "P2" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "sad" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "ctwinsize" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "hcwinsize" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "btclipvalue" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "maxdiff" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "uniquenessratio" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                    elif "scanlinesmask" in slide_edit._assignedLabel:
                        slide_edit.valueChanged.connect(self.updateStereoValues)
                except:
                    slide_edit.valueChanged.connect(self.saveValues)

        else:
            print ("No saved values so using default.")

    def _createSlideEdit(self, layout, label):
        slideEdit = SlideEdit()
        slideEdit._integerStep = True
        if(label == "hueMax" or label == "hueMin"):
            slideEdit._max = 180.0
            slideEdit._lockBounds = True
        else:
            slideEdit._max = 255.0
            slideEdit._lockBounds = True
        # slideEdit.setCurrentValue(50.5)
        index = self.ui_computerVision.missionList.currentIndex()
        slideEdit._assignedLabel = label + "_" + str(self.ui_computerVision.missionList.itemText(index))
        label = QtGui.QLabel(label)
        label.setStyleSheet('color: gold')
        layout.addWidget(label)
        layout.addWidget(slideEdit)
        # slideEdit.valueChanged.connect(self.updateMaxValues)
        self.slideEdits.append(slideEdit)

    def _setSlideEdits(self):
        """
        Places the slide edits in the layouts
        :return:
        """
        #print (self.labelList)
        # Loop through the different image processing layouts
        for i in range(0, len(self.layoutList)):
            if i == 0:
                # HSV Max
                for label in self.labelList[:3]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 1:
                # HSV Min
                for label in self.labelList[3:6]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 2:
                # Canny Edge
                for label in self.labelList[6:8]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 3:
                # Stereo Vision Layout 1
                for label in self.labelList[8:11]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 4:
                # Stereo Vision Layout 2
                for label in self.labelList[11:14]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 5:
                # Stereo Vision Layout 3
                for label in self.labelList[14:17]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 6:
                # Stereo Vision Layout 4
                for label in self.labelList[17:20]:
                    self._createSlideEdit(self.layoutList[i], label)
            elif i == 7:
                # Stereo Vision Layout 5
                for label in self.labelList[20:23]:
                    self._createSlideEdit(self.layoutList[i], label)


    def closeThread(self):
        self.computerVisionThread.cleanStop()
        self.startPressed = False

    @QtCore.pyqtSlot()
    def updateMaxValues(self):
        print("updating values")
        for slide_edit in self.slideEdits:
            if "hueMax" in slide_edit._assignedLabel:
                self.HSVMax[0] = int(slide_edit._currentValue)
            elif "saturationMax" in slide_edit._assignedLabel:
                self.HSVMax[1] = int(slide_edit._currentValue)
            elif "valueMax" in slide_edit._assignedLabel:
                self.HSVMax[2] = int(slide_edit._currentValue)
        '''
        if label == "hueMax":
            self.HSVMax[0] = value
        elif label == "saturationMax":
            self.HSVMax[1] = value
        elif label == "valueMax":
            self.HSVMax[2] = value
        '''
        self.emit(QtCore.SIGNAL("sendingHSVValues(PyQt_PyObject)"), [self.HSVMax, self.HSVMin])
        self.saveValues()

    @QtCore.pyqtSlot()
    def updateMinValues(self):
        for slide_edit in self.slideEdits:
            if "hueMin" in slide_edit._assignedLabel:
                self.HSVMin[0] = int(slide_edit._currentValue)
            elif "saturationMin" in slide_edit._assignedLabel:
                self.HSVMin[1] = int(slide_edit._currentValue)
            elif "valueMin" in slide_edit._assignedLabel:
                self.HSVMin[2] = int(slide_edit._currentValue)
        '''
        if label == "hueMin":
            self.HSVMin[0] = value
        elif label== "saturationMin":
            self.HSVMin[1] = value
        elif label== "valueMin":
            self.HSVMin[2] = value
        '''
        self.emit(QtCore.SIGNAL("sendingHSVValues(PyQt_PyObject)"), [self.HSVMax, self.HSVMin])
        self.saveValues()

    @QtCore.pyqtSlot()
    def updateCannyValues(self, label, value):
        if label == "thresholdMin":
            self.cannyEdge[0] = value
        elif label== "thresholdMax":
            self.cannyEdge[1] = value
        else:
            print ("labelpassed to updateCannyValues does not match predefined labels")

        self.saveValues()

    @QtCore.pyqtSlot()
    def updateStereoValues(self, label, value):
        if label== "uniqueness_ratio":
            self.stereoVision[9] = value
        elif label== "scanlines_mask":
            self.stereoVision[10] = value
        elif label== "hc_win_size":
            self.stereoVision[6] = value
        elif label== "bt_clip_value":
            self.stereoVision[7] = value
        elif label== "max_diff":
            self.stereoVision[8] = value
        elif label== "P2":
            self.stereoVision[3] = value
        elif label== "sad":
            self.stereoVision[4] = value
        elif label== "ct_win_size":
            self.stereoVision[5] = value
        elif label== "minDisparity":
            self.stereoVision[0] = value
        elif label== "maxDisparity":
            self.stereoVision[1] = value
        elif label== "P1":
            self.stereoVision[2] = value
        else:
            print (label)
            print ("labelpassed to updateStereoValues does not match predefined labels")

        self.saveValues()

    @QtCore.pyqtSlot()
    def startUsingSingleImage(self):
        # load an image to use:
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        # Sets dialog to open at a particular directory
        print ("Opening file dialog.")
        fileName = QtGui.QFileDialog.getOpenFileName(fileWidget, 'Open File', '/')
        try:
            if platform == "win32":
                fileName = fileName.replace('/', '\\')
            print "using: " + fileName
            self.imagePath = str(fileName)
            self.computerVisionThread.singleImage = cv2.imread(str(fileName))
            self.computerVisionThread.imagePath = str(fileName)
            self.ui_computerVision.imagePathLineEdit.setText(fileName)
            self.emit(QtCore.SIGNAL("loadedImage()"))
        except:
            print ("Image not found or not correct image format.")
        self.computerVisionThread.useImage = True
        self.computerVisionThread.useVideo = False
        self.computerVisionThread.useCameras = False

    @QtCore.pyqtSlot()
    def startUsingVideo(self):
        # load an image to use:
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        # Sets dialog to open at a particular directory
        print ("Opening file dialog.")
        fileName = QtGui.QFileDialog.getOpenFileName(fileWidget, 'Open File', '/')
        try:
            if platform == "win32":
                fileName = fileName.replace('/', '\\')
            print "using: " + fileName
            self.videoPath = fileName
            self.computerVisionThread.videoPath = fileName
            self.ui_computerVision.videoPathLineEdit.setText(fileName)
            self.emit(QtCore.SIGNAL("loadedImage()"))
        except:
            print ("Image not found or not correct image format.")
        self.computerVisionThread.useVideo = True
        self.computerVisionThread.useImage = False
        self.computerVisionThread.useCameras = False

    @QtCore.pyqtSlot()
    def saveValues(self):
        for slide_edit in self.slideEdits:
            self.externalComm.previous_state_logging.add(slide_edit._assignedLabel, str(slide_edit._currentValue))

    @QtCore.pyqtSlot()
    def update(self, frame):
        self.frame = frame
        height, width, channel = self.frame.shape
        bpl = 3 * width
        self.qImg = QImage(self.frame.data, width, height, bpl, QImage.Format_RGB888)
        pix = QtGui.QPixmap(self.qImg)
        
        self.ui_computerVision.Left_Camera.setPixmap(pix)
        self.ui_computerVision.Left_Camera.show()
        
    def debugThreadMessage(self, msg):
        print msg

    @QtCore.pyqtSlot()
    def hideSettings(self):
        print ("Should be hiding widget")
        if self.showSettings:
            self.ui_computerVision.hideSettingsButton.setText("Show Settings")
            self.ui_computerVision.settingsWidget.hide()
            self.showSettings = False
        else:
            self.ui_computerVision.hideSettingsButton.setText("Hide Settings")
            self.ui_computerVision.settingsWidget.show()
            self.showSettings = True

    @QtCore.pyqtSlot()
    def threadFinished(self, outputMessage):
        """
        Receive data from computer vision thread and
        restart thread.
        Signal: finished(QString) from computerVisionThread
        :param outputMessage: Message from the thread.
        :return:
        """
        self.computerVisionThread.wait()
        self.computerVisionThread.start()

    def startThread(self):
        """
        Starts computer vision thread.
        Gets called when widget opens.
        :return:  None
        """
        if not self.startPressed:
            """
            Start button isn't pressed so start thread.
            """
            if self.os == 'Linux-3.10.96-aarch64-with-Ubuntu-16.04-xenial':
                self.computerVisionThread.useTegra = True
            self.computerVisionThread.start()
            #self.ui_computerVision.startButton.setText("Stop")
            self.startPressed = True

        elif self.startPressed:
            """
            Start button is pressed again which means the user
            is trying to stop thread.
            """
            self.computerVisionThread.stop()
            self.startPressed = False
            #self.ui_computerVision.startButton.setText("Start")

class ComputerVisionThread(QtCore.QThread):
    """
    Worker thread specific for running computer vision tasks.
    """
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self.outputMessage = None
        self.obstacleLocation = None
        self._isRunning = True
        self.camera = None
        self.DEBUG = True
        self.imagePath = "lib/GuiComponents/ComputerVision/processed"
        self.imageReadNumber = 0
        self.videoPath = " "
        self.useVideo = False
        self.useCameras = False
        self.useImage = True
        self.useTegra = False
        self.singleImage = None
        self.HSVMax = [180,255,255]
        self.HSVMin = [0,0,0]
        
        while True:
            #imagePath = Path("Images/" + str(imageNumber) + ".JPEG")
            if not os.path.isfile("Saved_Images/" + str(self.imageReadNumber) + ".png"):
                break
            self.imageReadNumber += 1

        #self.context = fc2.Context() #Context to use PointGrey Cameras
        #self.imageContext = fc2.Image()


        '''if self.context.get_num_of_cameras() > 0:
            self.context.connect(*self.context.get_camera_from_index(0))
            self.context.set_format7_configuration(fc2.MODE_0, 0, 0, 808, 608, fc2.PIXEL_FORMAT_RGB8)
            self.context.start_capture()
            print "Connecting to camera..."
	else:
		print "No cameras available"'''

	for i in range(3):
		if os.path.isfile(self.imagePath + str(i) + ".png"):
			self.imageReadNumber = i
        
        self._connectSignals()

    def __del__(self):
        self.wait()

    def _connectSignals(self):
        """
        Connects signals to slots.

        signal --> slot

        sendingHSVValues (HSV values) --> updateHSVValues
        sendingCannyValues (Canny values) --> updateCannyValues
        sendingStereoValues (Stereo values) --> updateStereoValues

        :return:
        """
        self.connect(self.parent, QtCore.SIGNAL("sendingHSVValues(PyQt_PyObject)"), self._updateHSVValues)
        self.connect(self.parent, QtCore.SIGNAL("sendingCannyValues(PyQt_PyObject"), self._updateCannyValues)
        self.connect(self.parent, QtCore.SIGNAL("sendingStereValues(PyQt_PyObject"), self._updateStereoValues)

    def cleanStop(self):
        self._isRunning = False
        self.camera.release()

    def _updateStereoValues(self, Values):
        """
        Updates the stereo vision values.
        :param Values: List of stereo vision values.
        :return:
        """
        print ("Updating stereo values.")

    def _updateCannyValues(self, Values):
        """
        Updates the canny edge values.
        :param Values: List of canny edge values.
        :return:
        """
        print ("Updating canny values.")

    def _updateHSVValues(self, Values):
        """
        Updates the HSV values.
        :param Values: List of HSV Values
        :return:
        """
        #self.emit(QtCore.SIGNAL("debugThreadMessage(PyQt_PyObject)"), Values)
        self.HSVMax = Values[0]
        self.HSVMin = Values[1]

    def _updateVideo(self):
        """
        Updates the camera or video feed to run the next frame.
        Runs image processing on the new frame and updates the
        HUD.
        :return:
        """
        self.frame = []	
        if self.useVideo:
            if self.useTegra:
                self.frame = cv2.imread(self.videoPath)
            else:
                if self.camera == None:
                    self.camera = cv2.VideoCapture(self.videoPath)
                b, self.frame = self.camera.read()
        elif self.useCameras:
            print "Using cameras"	
            if self.useTegra:
                self.frame = cv2.imread(self.videoPath)
            else:
                if self.context.get_num_of_cameras() > 0:
                    self.context.retrieve_buffer(self.imageContext)
                    bgrFrame = np.array(self.imageContext)
                    self.frame = cv2.cvtColor(bgrFrame, cv2.COLOR_BGR2RGB)
		else:
			print "No Cameras Available"
        elif self.useImage:
        	if os.path.isfile(self.imagePath + str((self.imageReadNumber+2)%5) + ".png"):
        		#print "Image available, switching"
        		self.frame = cv2.imread(self.imagePath+str((self.imageReadNumber+1)%5) + ".png")
        		cv2.imwrite("Saved_Images/"+str((self.imageReadNumber+1))+".png", self.frame)
        		os.remove(self.imagePath + str(self.imageReadNumber%5) + ".png")
        		self.imageReadNumber = (self.imageReadNumber + 1)
        	else:
        		self.frame = cv2.imread(self.imagePath+str((self.imageReadNumber)%5) + ".png")
        		

        self.width = 808
        self.height = 608
        self.HUD = graphOver.GraphicOverlay(self, self.width, self.height)

        self.RGB = [160, 12, 45]
        if self.frame is None:
            #self.emit(QtCore.SIGNAL("debugThreadMessage(PyQt_PyObject)"), "Error Reading Frame")
            return
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(self.frame, np.array(self.HSVMin), np.array(self.HSVMax))
        self.frame = cv2.bitwise_and(self.frame, self.frame, mask = mask)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_HSV2RGB)

        self.left = self.frame
        self.right = self.frame[0:480, 640:1280]
        #self.left = self.frame
        #self.right = self.frame
        orientation = self.parent.externalComm.externalCommThread.orientation
        position = self.parent.externalComm.externalCommThread.position
	depth = self.parent.externalComm.externalCommThread.position[2]
        if self.parent.externalComm.missionPlanner.MovementController != None:
            thrusters = self.parent.externalComm.missionPlanner.MovementController.previousPwm
        else:   
            thrusters = [0,0,0,0,0,0,0,0]
        
        self.HUD.drawHeadingGauge(self.left, 10, 36, 1, 500, self.RGB, [orientation[0], orientation[0] + 10, orientation[0] - 20, orientation[0] + 30, orientation[0] + 40])
        self.HUD.drawPitchGauge(self.left, 10, 36, 600, self.RGB, [orientation[1], 30, 30, 30, 30])
        self.HUD.drawRollGauge(self.left, 10, 36, 0, 270, self.RGB, [orientation[2], 30, 30, 30, 30])
        self.HUD.drawDepthGauge(self.left, 10, 36, 1, 410, self.RGB, [depth, 0, [0, 0], 0, 0])
        self.HUD.drawAttitude(self.left, 40, 1, 0, 3, 3, self.RGB, [orientation, orientation, None, None, None],
                              [0, 0, 0], position, [0, 0,0])
        self.HUD.drawTemperature(self.left, 15, 3, self.RGB, 30)
        self.HUD.drawBatteryGauge(self.left, 80, 1, 1, self.RGB, [60, 60, 60, 60])
        self.HUD.drawMotorGauges(self.left, 40, 0, self.RGB, [thrusters[0],thrusters[1],thrusters[2],thrusters[3],thrusters[4],thrusters[5],thrusters[6],thrusters[7]], [1, 0, 1, 0, 1, 0, 1, 0])

        '''self.HUD.drawHeadingGauge(self.right, 10, 36, 1, 500, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawPitchGauge(self.right, 10, 36, 600, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawRollGauge(self.right, 10, 36, 0, 270, self.RGB, [30, 30, 30, 30, 30])
        self.HUD.drawDepthGauge(self.right, 10, 36, 1, 410, self.RGB, [30, 30, [30, 30], 30, 30])
        self.HUD.drawAttitude(self.right, 40, 1, 0, 3, 3, self.RGB, [[270, 90, 30], [270, 90, 30], None, None, None],
                              [360, 180, 120], [10, 20, 30], [0, 12, 0])
        self.HUD.drawTemperature(self.right, 15, 3, self.RGB, 30)
        self.HUD.drawBatteryGauge(self.right, 80, 1, 1, self.RGB, [60, 60, 60, 60])
        self.HUD.drawMotorGauges(self.right, 40, 0, self.RGB, [50, 50, 50, 50, 50, 50, 50, 50],
                                 [1, 0, 1, 0, 1, 0, 1, 0])'''

        #self.frame = np.hstack((self.left, self.right))

        self.emit(QtCore.SIGNAL("sendingVideo(PyQt_PyObject)"), self.frame)

    def run(self):
        #self.finished.connect(self.computerVisionClass.threadFinished())
#         while self._isRunning:
#             threadMessage = str(QtCore.QThread.currentThread()) + str(QtCore.QThread.currentThreadId())
#             self.outputMessage = threadMessage
#             self.updateVideo()
#              
        if self._isRunning:
            threadMessage = str(QtCore.QThread.currentThread()) + str(QtCore.QThread.currentThreadId())
            self.outputMessage = threadMessage
            self._updateVideo()
        self.emit(QtCore.SIGNAL('finished(QString)'), self.outputMessage)

