from PyQt4 import QtCore
from lib.Utils.loggingSystem import SubOutputLogging
from lib.GuiComponents.MissionCommander import missionCommander
import lib.Utils.utilities as utilities
import serial
# import microcontroller_tcb
# import microcontroller_hydras
# import microcontroller_pmud
# import microcontroller_sib
# import microcontroller_dib
import dvl
# import sparton_ahrs
# import movement
import math
import numpy as np
import copy
import struct
import previous_state_logging
import widget_config_logger
import time
import mission_planner_2
import mission_planner_3
from yoloPython import yoloComputerVision
import platform
import subprocess
import sparton_ahrs
import externalLoggingSystem
import glob
import displayArduino
import pressureArduino
import motherBoard as motherboard
import killSwitch
from serial.tools import list_ports as lp
import hydrasBoard



useMaestro = True

advM = utilities.AdvancedMath()
e1 = advM.e1  # Unit vector for x
e2 = advM.e2  # Unit vector for y
e3 = advM.e3  # Unit vector for z

controllerTimer = utilities.Timer()
controllerYawButtonReleaseTimer = utilities.Timer()
controllerDepthButtonReleaseTimer = utilities.Timer()


class ExternalComm(QtCore.QObject):
    """
    Part of the GUI thread.  This class acts as an intermediary for the gui thread
    and the embedded thread.  Use this class to pull data from the external devices
    then store that data in the class instances.  The gui classes can then call those
    instances.
    """

    def __init__(self, mainWindow):
        QtCore.QObject.__init__(self)
        self.mainWindowClass = mainWindow
        self.isDebug = True
        self.ahrsData = [0,0,0]
        self.dvlData = None
        self.computerVisionData = None
        self.sibData = None
        self.hydrasPingerData = None
        self.tcbData = None
        self.pmudData = None
        self.batteryVoltage = None
        self.pressureSensor = None
        self.externalCommThread = ExternalCommThread(self, mainWindow)
        #self.externalCommThread.initBackplaneComms()
        self.timer = QtCore.QTimer()
        self.guiDataToSend = {}
        self.cvDataToSend = {}
        self.dataChangedFromMap = False  # True if Data was change
        self.os = platform.platform()
        self.running = False
        self.missionPlanner = mission_planner_3.MissionPlanner(self)
        self.externalCommThread.missionPlanner = self.missionPlanner
        self.missionCommander = missionCommander.MissionCommander(self) #This is used JUST for saving missions after they have modified by the Map
        self.previous_state_logging = previous_state_logging.Previous_State_Logging("Previous_State_Save.csv")
        self.previous_state_logging.loadFile()
        self.widget_config_logging = widget_config_logger.Widget_Config_Logger(self.mainWindowClass)

    def connectSignals(self):
        """
        Starts the comm thread and connects signals to slots
        :return:
        """
        self.connect(self.externalCommThread, QtCore.SIGNAL("finished(PyQt_PyObject)"),
                     self.getExternalThreadData)
        self.connect(self.externalCommThread, QtCore.SIGNAL("requestGuiData()"),
                     self.sendGuiDataToExternalThread)
        self.connect(self.externalCommThread, QtCore.SIGNAL("requestCVData()"),self.sendCVDataToExternalThread)
        self.connect(self.missionPlanner, QtCore.SIGNAL("missionDebugMessage(PyQt_PyObject)"), self.writeMessage)
        self.missionPlanner.setMissionList(self.guiDataToSend["missionList"])
        self.missionPlanner.connectSignals()
        self.externalCommThread.connect(self.missionPlanner, QtCore.SIGNAL("currentMission(PyQt_PyObject)"), self.externalCommThread.setCurrentMission)
        self.externalCommThread.connect(self.mainWindowClass.debugValuesClass, QtCore.SIGNAL("debugPositionValues(PyQt_PyObject)"), self.externalCommThread.setDebugValues)

    def resetPosition(self):
        self.externalCommThread.position = [0,0,0]
        if self.externalCommThread.dvlResponseThread != None:
            self.externalCommThread.dvlResponseThread.getList = []

    def writeMessage(self, string):
        self.mainWindowClass.systemOutput.insertPlainText(string + "\n")

    def setWaypointX(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[0] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)

    def setWaypointY(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[1] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)
            

    def setWaypointZ(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            waypoint = None
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[2] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)
            

    def setWaypointOrientation_Yaw(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            waypoint = None
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[3] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)
            

    def setWaypointOrientation_Pitch(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            waypoint = None
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[4] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)
            

    def setWaypointOrientation_Roll(self, name, value):
        if "missionList" in self.guiDataToSend:
            missions = self.guiDataToSend["missionList"]
            waypoint = None
            for i,v in enumerate(missions):
                if name == v.parameters["name"]:
                    waypoint = v.generalWaypoint
                    waypoint[5] = value
            self.missionCommander.saveCurrentState()
            if waypoint != None:
                position = waypoint[:3]
                orientation = waypoint[3:]
                self.emit(QtCore.SIGNAL("waypointChanged(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), name, position, orientation)
            

    def changeDebug(self, var):
        self.isDebug = var
        self.externalCommThread.isDebug = var
        if var == False:
            #self.externalCommThread.__initSensors__()
            pass

    @QtCore.pyqtSlot()
    def sendCVDataToExternalThread(self):
        """
        Called when the external comm thread requests data.  This function
        then emits a signal with the Gui Data that will be sent to the
        external comm thread.
        :return:
        """

        self.cvDataToSend.update(self.mainWindowClass.getCVParams())
        if not self.running:
            return
        self.emit(QtCore.SIGNAL("getCVData(PyQt_PyObject)"), self.cvDataToSend)

    @QtCore.pyqtSlot()
    def sendGuiDataToExternalThread(self):
        """
        Called when the external comm thread requests data.  This function
        then emits a signal with the Gui Data that will be sent to the
        external comm thread.
        :return:
        """

        self.guiDataToSend.update(self.mainWindowClass.getGuiParams())
        if not self.running:
            return
        self.emit(QtCore.SIGNAL("getGuiData(PyQt_PyObject)"), self.guiDataToSend)
        

    @QtCore.pyqtSlot()
    def getExternalThreadData(self, externalProcessData):
        """
        Store data from thread and then start again
        Signal: self.externalCommThread on finished(Qstring)
        :param externalProcessData: All the external devices data in a list passed in from signal
        [self.ahrsGuiData, self.dvlGuiData, self.pmudGuiData, self.sibGuiData, self.hydrasPingerData])
        :return:
        """
        try:
            if not self.isDebug:
                self.ahrsData = externalProcessData[0]
                self.dvlData = externalProcessData[1]
                self.pmudData = externalProcessData[2]
                self.sibData = externalProcessData[3]
                self.hydrasPingerData = externalProcessData[4]
                self.emit(QtCore.SIGNAL("ExternalDataReady"))
            elif self.isDebug:
                #print "Getting Data: " + str(externalProcessData[0]) 
                self.ahrsData = externalProcessData[0]
                self.dvlData = externalProcessData[1]
                self.pmudData = externalProcessData[2]
                self.sibData = externalProcessData[3]
                self.hydrasPingerData = externalProcessData[4]
                self.emit(QtCore.SIGNAL("ExternalDataReady()"))
        except:
            pass

    def stopThread(self):
        self.externalCommThread.isRunning = False
        self.emit(QtCore.SIGNAL("stopThread"))
        self.missionPlanner.stopThread()


class ExternalCommThread(QtCore.QThread):
    """
    Separate thread to get all the external device data.  Also handles the actual navigation and
    movements of the sub.
    """

    def __init__(self, externalCommClass, mainWindow):
        """
        Initializes variables used in mission, such as sensors and thrusters, and variables taking in data from GUI thread.
        """
        import computer_vision_communication

        print ('%s, %s,' % (QtCore.QThread.currentThread(), int(QtCore.QThread.currentThreadId())))
        QtCore.QThread.__init__(self)
        self.externalCommClass = externalCommClass
        self.computerVisionComm = computer_vision_communication.ComputerVisionComm()
        self.computerVisionProcess = ComputerVisionProcess()
        
        self.mainWindow = mainWindow

	self.detectionDictionary = {"Dice 1":1, "Dice 2":2, "Dice 3":3, "Dice 4":4, "Dice 5":5, "Dice 6":6, "Qualificaiton Gate Top":16, "Qualification Gate Arm":15, "Entry Gate Top":18, "Entry Gate Arm":17}

        self.isRunning = True
	self.usingDebugValues = False
        self.prevAhrsData = None
        self.prevDvlData = None
        self.prevHydrasData = None
        self.ahrsData = [0, 0, 0]
        self.dvlData = [0, 0, 0,0]
        self.computerVisionData = [0, 0, 0, 0, 0]
        self.batteryVoltage = None
        self.pressureSensor = None
        self.maestroSerial = None
        self.arduinoSerial = None
        self.arduinoDisplaySerial = None
        self.arduinoDisplayData = None
        self.pressureArduinoDataPackets = None
        self.arduinoDisplayDataPackets = None
        self.startArduinoDisplay = time.time()

        self.isDebug = True
        self.runProcess = True
        self.missionSelectorData = None
        self.missions = None
        self.loggerIterationCounter = 0

        # For DVL
        self.dvlGuiData = [0, 0, 0, 0]
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.orientation = [0, 0, 0]
        self.dvlMiscData = [0, 0, 0]
        self.timeSinceLastComm = None
        self.clearDVLDataInitial = True
        self.dvlAhrsDummyThread = None
        self.dvlResponseThread = None


	#Mission Info
	self.currentMission = None

        # For AHRS
        self.ahrsData1 = [0, 0, 0]
        self.ahrsData2 = [0, 0, 0]
        self.ahrsData3 = [0, 0, 0]
        self.ahrsDataMedian = [0, 0, 0]
        self.ahrsGuiData = [0, 0, 0]
        self.spartonResponseThread1 = None
        self.spartonResponseThread2 = None
        self.spartonResponseThread3 = None
        self.spartonResponseList = [self.spartonResponseThread1, self.spartonResponseThread2, self.spartonResponseThread3]
        
        #For MotherBoard
        self.motherSerial = None
        self.motherPackets = None
        self.motherResponseThread = None
        self.motherMessage = None
        self.killSwitchInterrupt = False
        self.leakInterrupt = False
        self.depthInterrupt = False
        self.SIBInterrupt = False
        self.backplaneCurrentInterrupt = False
        self.autonomousModeOn = False
        
        #For Weapons
        self.weapon1On = False
        self.weapon2On = False
        self.weapon3On = False
        self.weapon4On = False
        self.weapon5On = False
        self.weapon6On = False
        self.weapon7On = False
        self.weapon8On = False
        self.weapon9On = False
        self.weapon10On = False
        self.weapon11On = False
        self.weapon12On = False
        self.weapon13On = False
        
        #For Kill Switch
        self.killSwitchSerial = None
        self.killSwitch = None
        self.killSwitchResponseThread = None
        self.kill = None

        # For SIB
        self.sibGuiData = [0, 0, 0]
        self.internalTemp1, self.internalTemp2, self.internalTemp3 = 0, 0, 0
        self.internalPressure1, self.internalPressure2, self.internalPressure3 = 0, 0, 0
        self.externalPressure1, self.externalPressure2, self.externalPressure3 = 0, 0, 0
        self.medianInternalTemp, self.medianInternalPressure, self.medianExternalDepth = 0, 0, 0

        # For HYDRAS
        self.hydrasSerial1 = None
        self.hydrasSerial2 = None
        self.hydrasResponseThread1 = None
        self.hydrasResponseThread2 = None
        self.hydrasHeading = None
        self.hydrasAltitude = None
        self.heading1, self.aoi1, self.confidence1 = 0, 0, 0
        self.heading2, self.aoi2, self.confidence2 = 0, 0, 0
        self.hydrasPingerData = [[0, 0, 0], [0, 0, 0]]

        # For Joystick Controller
        self.joystickGuiData = [None] * 9
        self.desiredMoveYaw, self.desiredMovePitch, self.desiredMoveRoll, self.desiredMoveDepth = 0, 0, 0, 0
        self.quickButtonPressYaw, self.quickButtonPressDepth, self.quickButtonPressOrientationLock = True, True, True
        self.toggleRightBumper = False
        self.setWaypoint = False
        self.removeWaypoint = False
        self.motorOffJoystickLock = True
        self.powerOnJoystickLock = False


        # GUI data
        self.guiData = {}
        self.cvData = {}
        self.prevData = {}


	#Computer Vision Stuff
        self.cvData = {
            'useImage': False, 'useVideo': False,'useCameras':True, "frameSkip":"0",
            'imagePath':'i','videoPath': 'v'}
        self.computerVisionConnected = True
	self.yoloPython = yoloComputerVision()
	self.yoloPython.start()
        self.detectionData = {}
        #self.detectionData["classNumbers"] = []
        self.frameSkip = 15
    
        self.__initSensors__()
        self.connectSignals()



    def stopThread(self):
        self.isRunning = False

    def setCurrentMission(self, mission):
        if mission == "None":
            return
        self.currentMission = mission
		

    def __initSensors__(self):
        """
        Initialized sensors and data packets to be ran in the run loop.
        :return:
        """
	print "Starting Backplane Comms..."
        try:
			
			self.motherSerial = serial.Serial("/dev/ttyUSB0", 9600)
			self.motherPackets = motherboard.motherBoardDataPackets(self.motherSerial)
			
			self.motherResponseThread = motherboard.motherBoardResponse(self.motherSerial)
			self.motherResponseThread.start()
			
        except:
            print "Unable to connect to Mother Board" 
        if True or platform.platform() == 'Linux-4.4.15-aarch64-with-Ubuntu-16.04-xenial':
               self.computerVisionProcess.start()
               pass
        else:
               self.computerVisionConnected = False
        if False:
			try:
				self.killSwitchSerial = serial.Serial("/dev/ttyACM9", 9600)
			except:
				print "Unable to connect to Kill Switch"
				
        '''if useMaestro:
            try:
                self.maestroSerial = serial.Serial("/dev/ttyACM2", 9600)
                pass
            except:
                print "Unable to connect to Maestro"
        else:
            pass'''
            
        try:
            maestroPort = None			
            available_ports = lp.comports()
            for port in available_ports:
                description = str(port[1])
                
                if description.startswith("Pololu"):
                    if maestroPort == None:
                        maestroPort = port[0]
                    elif (int(port[0][-1:]) < int(maestroPort[-1:])):
                        maestroPort = port[0]
            self.maestroSerial = serial.Serial(maestroPort, 9600)
        except:
            self.maestroSerial = serial.Serial("/dev/ttyACM1", 9600)			                						     																		    
            print "Maestro was not found"
            
        if False:
            try:
                self.arduinoSerial = serial.Serial("/dev/ttyACM2", 9600)
                self.pressureArduinoDataPackets = pressureArduino.pressureResponse(self.arduinoSerial)
                self.pressureArduinoDataPackets.start()
            except:
                print "Unable to connect to Arduino for pressure"
        else:
            pass
        
        if True:
            try:
                self.arduinoDisplaySerial = serial.Serial("/dev/ttyACM0", 115200)
                self.arduinoDisplayDataPackets = displayArduino.displayArduino(self.arduinoDisplaySerial)
            except:
                print "Unable to connect to Arduino for display"
        else:
            pass

        # DVL initialization
        try:
			
            DVLComPort = serial.Serial("/dev/ttyUSB1", 115200)
            self.dvlDataPackets = dvl.DVLDataPackets(DVLComPort)
            self.dvlResponseThread = dvl.DVLResponse(DVLComPort)
            self.dvlResponseThread.start()
            
            '''dvlAhrsComPort = serial.Serial("/dev/ttyUSB6", 38400)
            self.dvlAhrsDummyThread = dvl.AHRSDummyCommunicator(dvlAhrsComPort)
            self.dvlAhrsDummyThread.start()'''
            
            
        except:
            print "Unable to connect to DVL"
            
        try:
            # AHRS initializing
            # Need to put the correct comm ports in 
            self.spartonResponseThread1 = sparton_ahrs.SpartonAhrsResponse("/dev/ttyUSB3")
            self.spartonResponseThread1.start()
            
        except:
            print "Unable to connect to AHRS1"
            
        try:
            pass
            #self.spartonResponseThread2 = sparton_ahrs.SpartonAhrsResponse("/dev/ttyUSB6")
            #self.spartonResponseThread2.start()
            
        except:
            print "Unable to connect to AHRS2"
        
        try:    
			pass
            #self.spartonResponseThread3 = sparton_ahrs.SpartonAhrsResponse("/dev/ttyUSB1")
            #self.spartonResponseThread3.start()   
        
        except:
            print "Unable to connect to AHRS3"
        
        
		#Pitch
        try:
            pass
            #self.hydrasSerial1 = serial.Serial("/dev/ttyUSB2", 115200)
            #self.hydrasResponseThread1 = hydrasBoard.hydrasBoardResponseThread(self.hydrasSerial1)
            #self.hydrasResponseThread1.start()
        except:    	
            print "Unable to connect to Hydras1"
        
        
        #Heading
        try:
            pass
            self.hydrasSerial2 = serial.Serial("/dev/ttyUSB7", 115200)
            self.hydrasResponseThread2 = hydrasBoard.hydrasBoardResponseThread(self.hydrasSerial2)
            self.hydrasResponseThread2.start()
        except:    	
            print "Unable to connect to Hydras2"
            
        '''
        Not using the other two AHRS on the testbed 
        self.spartonResponseThread2 = sparton_ahrs.SpartonAhrsResponse()
        self.spartonResponseThread2.start()
        self.spartonResponseThread3 = sparton_ahrs.SpartonAhrsResponse()
        self.spartonResponseThread3.start()
        '''


    def connectSignals(self):
        """
        getGuiData ---> emitted by externalCommClass with guiData list ---> getGuiData slot
        :return:
        """
        self.connect(self.externalCommClass, QtCore.SIGNAL("getGuiData(PyQt_PyObject)"),
                     self.getGuiData)
        self.connect(self.externalCommClass, QtCore.SIGNAL("getCVData(PyQt_PyObject)"),
                     self.getCVData)
        self.connect(self.externalCommClass, QtCore.SIGNAL("stopThread"), self.stopThread)
        
    def setDebugValues(self, data):
	self.usingDebugValues = True
        self.position = data[:3]
        self.orientation = data[3:]

    @QtCore.pyqtSlot()
    def getGuiData(self, guiData):
        self.guiData = guiData

    @QtCore.pyqtSlot()
    def getCVData(self, cvData):
        self.cvData = cvData

    def cleanStop(self):
        """
        Function which cleanly stops the thread.  Stops
        all child threads and clean power's down the sub.
        :return:
        """
        self.isRunning = False
	self.yoloPython.killThread()
        if self.spartonResponseThread1 != None:
        	self.spartonResponseThread1.killThread()
        if self.spartonResponseThread2 != None:
        	self.spartonResponseThread2.killThread()
        if self.spartonResponseThread3 != None:
        	self.spartonResponseThread3.killThread()
        	
        if self.dvlResponseThread != None:
        	self.dvlResponseThread.killThread()
        if self.dvlAhrsDummyThread != None:
        	self.dvlAhrsDummyThread.killThread()
        	
        if self.pressureArduinoDataPackets != None:
        	self.pressureArduinoDataPackets.killThread()
        	
        if self.motherResponseThread != None:
			self.motherResponseThread.killThread()
        if self.missionPlanner != None:
			self.missionPlanner.stopThread()
        if self.hydrasResponseThread1 != None:
            self.hydrasResponseThread1.killThread()	
        if self.hydrasResponseThread2 != None:
            self.hydrasResponseThread2.killThread()	    				
        

    def run(self):
        # AHRS
        self.isRunning = True
        count = 0
        #self.computerVisionProcess.start()

        # Logging System
        # Search through the directory we're in to find the next highest number for the file name.
        highestNum = 0
        for file in glob.glob('*.csv'):
            if file.startswith("exLog"):
                currentNum = int(file[5:-4])
                if currentNum > highestNum:
                    highestNum = currentNum

        highestNum += 1

        self.fileName = 'exLog' + str(highestNum)
        #self.log = externalLoggingSystem.exLog(self.fileName)
        startTime = time.time()
        while self.isRunning:
            time.sleep(.01)
            if not self.isDebug:
                # Write to the log file every tenth of a second
                if time.time() - startTime >= .1:
                    #print "Calling writeData()"
                    #self.writeData()
                    startTime = time.time()
                
                #self.emit(QtCore.SIGNAL("requestCVData()"))
                self.emit(QtCore.SIGNAL("requestGuiData()"))
                
                self.computerVisionComm.setParameters(self.cvData)

                # Send data over sockets
                if self.computerVisionConnected:
                	self.computerVisionComm.sendParameters()

                self.getSensorData()
                self.emit(QtCore.SIGNAL("requestCurrentMission"))
                self.emit(QtCore.SIGNAL("Data Updated"))
                #self.detectionData = self.computerVisionComm.detectionData
		if len(self.yoloPython.getList) > 0:
			detectionData = self.yoloPython.getList.pop()
			fixedDetections = []
			for det in detectionData:
				classNum = self.detectionDictionary[det[0]]
				pos = det[2]
				fixedDetections.append([classNum, pos[0], pos[1], pos[2], pos[3]])
			self.detectionData = fixedDetections
				
				
			
			
                data = {"ahrs": self.ahrsData, "dvl": self.dvlGuiData, 
                        "sib": self.sibGuiData,
                        "hydras": self.hydrasPingerData}

                self.emit(QtCore.SIGNAL("finished(PyQt_PyObject)"), data)
                if self.currentMission != None:
                    self.emit(QtCore.SIGNAL("gotPositionData(PyQt_PyObject, PyQt_PyObject)"), self.position+self.orientation, self.currentMission.generalWaypoint)
            else:
                #self.emit(QtCore.SIGNAL("requestCVData()"))
                #print "Test:  " + str(self.cvData)
                self.computerVisionComm.setParameters(self.cvData)
                if self.computerVisionConnected:
                	self.computerVisionComm.sendParameters()

                self.detectionData = self.computerVisionComm.detectionData
                self.getSensorData()
                self.emit(QtCore.SIGNAL("Data Updated"))
                self.emit(QtCore.SIGNAL("requestCurrentMission"))
                if self.currentMission != None:
                    self.emit(QtCore.SIGNAL("gotPositionData(PyQt_PyObject, PyQt_PyObject)"), self.position+self.orientation, self.currentMission.generalWaypoint)
		
		# Reconnect to the maestro after the kill switch
		'''
		try:
			self.maestroSerial.write(' ')
		except:
			#print "Couldn't write to maestro!, trying to reconnect"
			try:
				ports = glob.glob("/dev/ttyACM*")
				maestroPort =  None
				maestroPortNumber = 0
				for port in ports:
					#print "Trying port: ", port
					portNumber = int(port[11:])
					if portNumber <= maestroPortNumber:
						maestroPort = port
						maestroPortNumber = portNumber
				#print "Using port: ", maestroPort
				self.maestroSerial.close()
				self.maestroSerial = serial.Serial(maestroPort, 9600)
				#print "Connected to maestro after killing!"
			except:
				pass
				#print "Couldn't connect to maestro after killing."
		'''
		#print self.detectionData
                
                self.emit(QtCore.SIGNAL("requestGuiData()"))
                
                data = {"ahrs": self.ahrsGuiData, "dvl": self.dvlGuiData, 
                        "sib": self.sibGuiData,
                        "hydras": self.hydrasPingerData}
                
                if data != self.prevData:
                    self.prevData = data
                    self.emit(QtCore.SIGNAL("finished(PyQt_PyObject)"), data)

        self.mainWindow.gui.processEvents()
                    
    def calculateMedianAhrs(self, ahrsData1, ahrsData2, ahrsData3):
        '''
        Calculates the median values of the AHRS data to minimize error.
        
        **Parameters**: \n
        * **ahrsData1** - Latest AHRS orientation data.
        * **ahrsData2** - Latest AHRS orientation data.
        * **ahrsData3** - Latest AHRS orientation data.
        
        **Returns**: \n
        * **ahrsDataMedian** - Median AHRS orientation data.\n
        '''
        radToDeg = 180/3.1415926535
        degToRad = 3.1415926535/180
        
        angleAhrs12 = math.acos(round(math.cos(ahrsData1[0]*degToRad)*math.cos(ahrsData2[0]*degToRad) + math.sin(ahrsData1[0]*degToRad)*math.sin(ahrsData2[0]*degToRad), 3))*radToDeg #dot product
        angleAhrs13 = math.acos(round(math.cos(ahrsData1[0]*degToRad)*math.cos(ahrsData3[0]*degToRad) + math.sin(ahrsData1[0]*degToRad)*math.sin(ahrsData3[0]*degToRad), 3))*radToDeg #dot product
        angleAhrs23 = math.acos(round(math.cos(ahrsData2[0]*degToRad)*math.cos(ahrsData3[0]*degToRad) + math.sin(ahrsData2[0]*degToRad)*math.sin(ahrsData3[0]*degToRad), 3))*radToDeg #dot product
        
        if angleAhrs12 >= angleAhrs13 and angleAhrs12 >= angleAhrs23:
            medianHeading = ahrsData3[0]
        elif angleAhrs13 >= angleAhrs12 and angleAhrs13 >= angleAhrs23:
            medianHeading = ahrsData2[0]
        elif angleAhrs23 >= angleAhrs12 and angleAhrs23 >= angleAhrs13:
            medianHeading = ahrsData1[0]
            
        medianPitch = numpy.median(numpy.array([ahrsData1[1], ahrsData2[1], ahrsData3[1]]))
        
        medianRoll = numpy.median(numpy.array([ahrsData1[2], ahrsData2[2], ahrsData3[2]]))
        
        ahrsDataMedian = [medianHeading, medianPitch, medianRoll]
        
        return ahrsDataMedian

    def getSensorData(self):
	if self.usingDebugValues == True:
		return

        #print "Getting Sensor Data"
        if self.killSwitchSerial != None:
            while (self.killSwitchResponseThread.getList) > 0:
                self.killData = self.killSwitchResponseThread.pop(0)
                self.kill = self.killData[0]
                
                if self.kill:
                    self.mainWindow.stopPressed()
                self.batteryVoltage = self.killData[1]
                self.batteryCurrent = self.killData[2]
                    
        if self.spartonResponseThread1 != None:
            while len(self.spartonResponseThread1.getList) > 0:
				self.ahrsData1 = self.spartonResponseThread1.getList.pop(0)
				
				#I'm rotating the output of the AHRS because the AHRS merger is facing the wrong way
				'''Rotation Matrix = [[-1, 0, 0],
				                      [ 0, 1, 0],
									  [ 0, 0, 1]]'''
				
				self.ahrsData1[1] = -self.ahrsData1[1] + 5
				self.ahrsData1[2] = -self.ahrsData1[2]
				self.ahrsData1[0] = (self.ahrsData1[0] + 180) %360
                #self.ahrsData1[0] = (self.ahrsData1[0] + 169)%360
        if self.spartonResponseThread2 != None:
            while len(self.spartonResponseThread2.getList) > 0:
                self.ahrsData2 = self.spartonResponseThread2.getList.pop(0)
        if self.spartonResponseThread3 != None:
            while len(self.spartonResponseThread3.getList) > 0:
                self.ahrsData3 = self.spartonResponseThread3.getList.pop(0)
            self.ahrsData3[2]
        

        #self.ahrsData = self.calculateMedianAhrs(self.ahrsData1, self.ahrsData2, self.ahrsData3)
        self.ahrsData = self.ahrsData1
        if self.spartonResponseThread1 != None:
            self.orientation = self.ahrsData
        #self.ahrsData[0] = 0
        #print "AHRS", self.ahrsData
			#print int(self.ahrsData1[0]), int(self.ahrsData2[0]), int(self.ahrsData3[0])
        #print self.ahrsData1[0], self.ahrsData2[0], self.ahrsData3[0]
        #print self.ahrsData
        #self.ahrsData = self.ahrsData2
        #print self.ahrsData1
        if self.motherPackets != None:
	    self.motherPackets.sendSIBPressureRequest()
            self.motherPackets.sendBMSVoltageRequest()
        if self.motherResponseThread != None:
            while len(self.motherResponseThread.getList) > 0:
                self.motherMessage = self.motherResponseThread.getList.pop(0)
                if len(self.motherMessage) == 0: 
                    continue
                '''if(self.motherMessage[0] == 8): # Kill Switch Interrupt
                    self.killSwitchInterrupt = True
                elif(self.motherMessage[0] == 16): # Leak interrupt
                    self.leakInterrupt = True
                elif(self.motherMessage[0] == 24): # Depth interrupt
                    self.depthInterrupt = True
                elif(self.motherMessage[0] == 104): # Backplane Current interrupt
                    self.backplaneCurrentInterrupt = True
                elif(self.motherMessage[0] == 112): # Autonomous Mode
                    self.mainWindow.startPressed()#self.autonomousModeOn = True
                    #previousAuto = self.autonomousModeOn
                    #self.autonomousModeOn = not(self.autonomousModeOn)
                    #if(previousAuto == False & self.autonomousModeOn == True):
                    #    self.mainWindow.startPressed()
                elif(self.motherMessage[0] == 224): # Weapon 1 on
                    self.weapon1On = True
                elif(self.motherMessage[0] == 232): # Weapon 2 on
                    self.weapon2On = True
                elif(self.motherMessage[0] == 240): # Weapon 3 on
                    self.weapon3On = True
                elif(self.motherMessage[0] == 248): # Weapon 4 on
                    self.weapon4On = True          
                elif(self.motherMessage[0] == 256): # Weapon 5 on
                    self.weapon5On = True
                elif(self.motherMessage[0] == 264): # Weapon 6 on
                    self.weapon6On = True
                elif(self.motherMessage[0] == 272): # Weapon 7 on
                    self.weapon7On = True
                elif(self.motherMessage[0] == 280): # Weapon 8 on
                    self.weapon8On = True
                elif(self.motherMessage[0] == 288): # Weapon 9 on
                    self.weapon9On = True
                elif(self.motherMessage[0] == 296): # Weapon 10 on
                    self.weapon10On = True
                elif(self.motherMessage[0] == 304): # Weapon 11 on
                    self.weapon11On = True
                elif(self.motherMessage[0] == 312): # Weapon 12 on
                    self.weapon12On = True
                elif(self.motherMessage[0] == 320): # Weapon 13 on
                    self.weapon13On = True'''
                if(self.motherMessage[0] == 392): # SIB Pressure
                    depth1 = self.motherMessage[1]
                    #depth2 = self.motherMessage[2]
                    depth3 = self.motherMessage[3]
                    depth = np.median([depth3])
                    self.position[2] = float((depth-95))/9.2
                if(self.motherMessage[0] == 656):
                    if self.mainWindow.subwin_mainWidget.debugCheck.isChecked():
			    print "Starting autonomous..."
			    self.mainWindow.subwin_mainWidget.debugCheck.setChecked(False)
                            self.mainWindow.changeText()
			    self.mainWindow.startPressed()
                elif(self.motherMessage[0] == 648):#Voltage Data	
					self.batteryVoltage = self.motherMessage[1]
                #print self.motherMessage

        if self.hydrasResponseThread1 != None:
            while len(self.hydrasResponseThread1.getList):
                hydrasData1 = self.hydrasResponseThread1.getList.pop(0)
                if hydrasData1[0] == 1:
                    self.hydrasHeading = hydrasData1[1]
                else:
                    self.hydrasAltitude = hydrasData1[1]									
                
        if self.hydrasResponseThread2 != None:
            while len(self.hydrasResponseThread2.getList):
                hydrasData2 = self.hydrasResponseThread2.getList.pop(0)
                if hydrasData2[0] == 1:
                    self.hydrasHeading = hydrasData2[1]
                else:
                    self.hydrasAltitude = hydrasData2[1]
        #print "Hydras Data: ", self.hydrasHeading     
        		
        if self.dvlResponseThread != None:
            fakeData = [self.ahrsData[0], self.ahrsData[1], self.ahrsData[2]]
            #fakeData[0] = (fakeData[0]+270)%360
            #self.dvlAhrsDummyThread.updateAhrsValues(self.ahrsData)
            self.getDVLData(self.ahrsData)
            #print "Overwritting DVL data to prevent sub from \"pointing\" towards waypoint"
        
        '''
            if self.dvlAhrsDummyThread != None:
                self.dvlAhrsDummyThread.updateAhrsValues(self.ahrsData)
                self.dvlGuiData = self.getDVLData(self.ahrsGuiData)
        '''

        '''
           if self.arduinoSerial != None:
               while self.arduinoSerial.inWaiting():
                   pressureData = 0
                   try:
                       pressureData = int(self.arduinoSerial.readline())
                       self.arduinoSerial.flushInput()
                       #print pressureData
                   except:
                       print "Arduino gave a weird character"
                   pressureDataNew = numpy.interp(pressureData, [670, 790], [0, 9])
                   #self.position[2] = (((pressureData*77)/1023)-14.7)/0.4335
                   #depth = ((pressureDataIn/MaximumPressureData)*TransducerMax) - 1ATM(14.7) -Unknonwn Error /Density of water
        depthError = 20.7 #Depth errror, needs to be changed per pool... Lowering the number makes the sub think its starting lower               
        depth = (((pressureData/1023.0)*30.0)-depthError)/(0.466) 
        '''
                
        if self.pressureArduinoDataPackets != None:
            while len(self.pressureArduinoDataPackets.getList) > 0:
                depth = self.pressureArduinoDataPackets.getList.pop(0)
                if not abs(self.position[2] - depth) > 5 and depth > -2:
                    self.position[2] = depth
                else:
                    print depth
                #print depth
                
                #print self.ahrsData, self.position[2]
        if True or self.isDebug: 
            pass      
            #print self.detectionData
            #print self.orientation, self.position
            #print self.position[2]
                
                #print self.position
                
                
        self.ahrsGuiData = self.ahrsData

        '''
        # Send data to the arduino that controls display inside the sub
        startArduinoDisplay = time.time()
        if self.arduinoDisplayDataPackets != None and time.time() - startArduinoDisplay > 1:
            depth = str(int(self.position[2]))
            waypointN = str(int(self.position[0]))
            waypointE = str(int(self.position[1]))
            waypointUp = str(int(self.position[3]))
            yaw = str(int(self.orientation[0]))
            pitch = str(int(self.orientation[1]))
            roll = str(int(self.orientation[2]))
            mission = 0
            
            self.arduinoDisplayDataPackets.sendToDisplay(depth, waypointN, waypointE, waypointUp, yaw, pitch, roll, mission)
            startArduinoDisplay = time.time()'''
        depth = str(int(self.position[2]))
        waypointN = str(int(self.position[0]))
        waypointE = str(int(self.position[1]))
        waypointUp = str(int(self.position[2]))
        yaw = str(int(self.orientation[0]))
        pitch = str(int(self.orientation[1]))
        roll = str(int(self.orientation[2]))
        mission = "Percy is lit"

        # Send data to the arduino that controls display inside the sub
        if self.arduinoDisplayDataPackets != None and time.time() - self.startArduinoDisplay > 1:
            if self.arduinoDisplayData == None:
                self.arduinoDisplayData = [depth]
                self.arduinoDisplayData.append(waypointN)
                self.arduinoDisplayData.append(waypointE)
                self.arduinoDisplayData.append(waypointUp)
                self.arduinoDisplayData.append(yaw)
                self.arduinoDisplayData.append(pitch)
                self.arduinoDisplayData.append(roll)
                self.arduinoDisplayData.append(mission)
            else:
                self.arduinoDisplayData[0] = depth
                self.arduinoDisplayData[1] = waypointN
                self.arduinoDisplayData[2] = waypointE
                self.arduinoDisplayData[3] = waypointUp
                self.arduinoDisplayData[4] = yaw
                self.arduinoDisplayData[5] = pitch
                self.arduinoDisplayData[6] = roll
                self.arduinoDisplayData[7] = mission
            self.arduinoDisplayDataPackets.sendToDisplay(self.arduinoDisplayData)
            self.startArduinoDisplay = time.time()

    def getDVLData(self, ahrsData):
        if self.timeSinceLastComm == None:
            self.timeSinceLastComm = time.time()
        """
        Communicates with the boards to accept sensor, feedback, control the SUB's movement, and communicate with the GUI
        :param ahrsData: Orientation data from the AHRS
        :return: [Position, velocity, orientation, and other data detected by DVL]
        """
        while len(self.dvlResponseThread.getList) > 0:
            #print "Got DVL Data"
            ensemble = self.dvlResponseThread.getList.pop(0)

            try:
                xVel, yVel, zVel = ensemble[0]
                self.velocity = [xVel, yVel, zVel]
                heading = ahrsData[0]
                timeVelEstX, timeVelEstY, timeVelEstZ = ensemble[1]
                timeDifference = self.timeSinceLastComm - time.time()
                timeDifference = 1/float(8)
                timeVelEstX = timeDifference
                timeVelEstY= timeDifference
                timeVelEstZ = timeDifference
                #print "Values are", self.velocity, ensemble[1]
                #Probably have to fix the following equations
                if not(xVel < -32):# If no error in DVL, indicated by velocity being less than 32
                    degToRad = 3.1415926535 / 180
                    velNcompX = (xVel) * (math.cos(math.radians(heading)))
                    velNcompY = (yVel) * (math.sin(math.radians(heading)))

                    velEcompX = (xVel) * -(math.sin(math.radians(heading)))
                    velEcompY = (yVel) * (math.cos(math.radians(heading))) 

                    '''velNcompX = xVel * math.cos(heading * degToRad)
                    velNcompY = yVel * math.sin(heading *degToRad)
           
                    velEcompX = xVel * math.sin(heading * degToRad)
                    velEcompY = yVel * math.cos(heading * degToRad)'''


                    lastDistanceTraveledN = (velNcompX * timeVelEstX) + (
                                velNcompY * timeVelEstY)#  1000 / 1.74
                    lastDistanceTraveledE = (velEcompX * timeVelEstX) + (
                                velEcompY * timeVelEstY)# * 1000 / 1.74
                    lastDistanceTraveledD = zVel * timeVelEstZ

                    #Add distance traveled to last known position
                    #North
		    #Equation works for north component using East equation
                    self.position[0] = self.position[0] - (lastDistanceTraveledE * float(73)/float(21))
                    #East
                    self.position[1] = self.position[1] - (lastDistanceTraveledN * float(73)/float(21))

                else:
                    print "DVL Error"
                    northPosition, eastPosition, upPosition, positionError = 0, 0, 0, 0
                    xVel, yVel, zVel = 0, 0, 0
                    heading, pitch, roll, depth = 0, 0, 0, 0
                    elevation, speedOfSound, waterTemp = 0, 0, 0

            except Exception as e:
                print "DVL Exception: ", str(e)
                northPosition, eastPosition, upPosition, positionError = 0, 0, 0, 0
                xVel, yVel, zVel = 0, 0, 0
                heading, pitch, roll, depth = 0, 0, 0, 0
                elevation, speedOfSound, waterTemp = 0, 0, 0

        return [self.position, self.velocity, self.orientation, self.dvlMiscData]

    def writeData(self):
        # If all of the data has not changed, do not write to the file.
        if self.prevAhrsData == self.orientation and self.prevDvlData == self.position:
            pass
        else:
            self.prevAhrsData = self.orientation
            self.prevDvlData = self.position
            self.prevHydrasData = self.hydrasPingerData

            # TODO: Include hydras data too.
            #print "Calling writeToFile()"
            #self.log.writeToFile(self.position, self.orientation)

    def calculateMedianAhrs(self, ahrsData1, ahrsData2, ahrsData3):
        """
        Calculates the median values of the AHRS data to minimize error
        :param ahrsData1: Latest AHRS orientation data
        :param ahrsData2: Latest AHRS orientation data
        :param ahrsData3: Latest AHRS orientation data
        :return: Median AHRS orientation data
        """
        radToDeg = 180 / 3.1415926535
        degToRad = 3.1415926535 / 180

        angleAhrs12 = math.acos(round(math.cos(ahrsData1[0] * degToRad) * math.cos(ahrsData2[0] * degToRad) + math.sin(
            ahrsData1[0] * degToRad) * math.sin(ahrsData2[0] * degToRad), 3)) * radToDeg  # dot product
        angleAhrs13 = math.acos(round(math.cos(ahrsData1[0] * degToRad) * math.cos(ahrsData3[0] * degToRad) + math.sin(
            ahrsData1[0] * degToRad) * math.sin(ahrsData3[0] * degToRad), 3)) * radToDeg  # dot product
        angleAhrs23 = math.acos(round(math.cos(ahrsData2[0] * degToRad) * math.cos(ahrsData3[0] * degToRad) + math.sin(
            ahrsData2[0] * degToRad) * math.sin(ahrsData3[0] * degToRad), 3)) * radToDeg  # dot product

        if angleAhrs12 >= angleAhrs13 and angleAhrs12 >= angleAhrs23:
            medianHeading = ahrsData3[0]
        elif angleAhrs13 >= angleAhrs12 and angleAhrs13 >= angleAhrs23:
            medianHeading = ahrsData2[0]
        elif angleAhrs23 >= angleAhrs12 and angleAhrs23 >= angleAhrs13:
            medianHeading = ahrsData1[0]

        medianPitch = numpy.median(numpy.array([ahrsData1[1], ahrsData2[2], ahrsData3[1]]))
        medianRoll = numpy.median(numpy.array([ahrsData1[2], ahrsData2[2], ahrsData3[2]]))

        ahrsDataMedian = [medianHeading, medianPitch, medianRoll]

        return ahrsDataMedian


class ComputerVisionProcess(QtCore.QThread):
    def __init__(self):
        super(ComputerVisionProcess, self).__init__()
        self.os = platform.platform()

    def run(self):
        if False or self.os == 'Linux-4.4.15-aarch64-with-Ubuntu-16.04-xenial':
            print "Starting computer vision process..."
            subprocess.call('/media/sub_data/robosub-2018/MechaVision/yolo_cpp/MechaVision')
