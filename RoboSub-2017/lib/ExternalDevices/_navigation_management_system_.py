'''
Copyright 2014, Austin Owens, All rights reserved.

.. module:: _navigation_management_system_
   :synopsis: Handles navigation, external device communication, and missions.
   
:Author: Austin Owens <sdsumechatronics@gmail.com>
:Date: Created on Oct 24, 2014
:Description: Defines process which will communicate with GUI to drive Sub based on mission parameters or Manual Control.
'''
import time, sys
import serial
import numpy
import mission_planner
import math
import struct
import main.utility_package.utilities as utilities
import copy

useArduino = True

advM = utilities.AdvancedMath()
e1 = advM.e1 #Unit vector for x
e2 = advM.e2 #Unit vector for y
e3 = advM.e3 #Unit vector for z

controllerTimer = utilities.Timer()
controllerYawButtonReleaseTimer = utilities.Timer()
controllerDepthButtonReleaseTimer = utilities.Timer()

#logger = DataLog()
            
class NavigationManagementSystem():
    '''
    Process which handles the actual navigation and movements of the sub, including interactions with the hardware.
    '''
    def __init__(self):
        '''
        Initializes variables used in missions, such as sensors and thrusters, and variables taking in data from the GUI process.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        #For NMS
        self.runProcess = True
        self.guiData = [True, None, None, None, None] #True initially. The size of self.guiData will dynamically update later in the code depending on how big the array is that the GUI side is sending over
        self.missionSelectorData = None
        self.missions = None
        self.loggerIterationCounter = 0
        
        #For DVL
        self.dvlGuiData = [0, 0, 0, 0]
        self.position = [0, 0, 0, 0]
        self.velocity = [0, 0, 0]
        self.orientation = [0, 0, 0, 0]
        self.dvlMiscData = [0, 0, 0]
        self.clearDVLDataInitial = True
        
        #For AHRS
        self.ahrsData1 = [0, 0, 0]
        self.ahrsData2 = [0, 0, 0]
        self.ahrsData3 = [0, 0, 0]
        self.ahrsDataMedian = [0, 0, 0]
        
        #For TCB
        self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
        self.tcb1Motor1Payload = [0, 0, 0]
        self.tcb1Motor2Payload = [0, 0, 0]
        self.tcb1Motor3Payload = [0, 0, 0]
        self.tcb1Motor4Payload = [0, 0, 0]
        self.tcb2Motor1Payload = [0, 0, 0]
        self.tcb2Motor2Payload = [0, 0, 0]
        self.tcb2Motor3Payload = [0, 0, 0]
        self.tcb2Motor4Payload = [0, 0, 0]
        self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
        
        #For PMUD
        self.pmudGuiData = [0, 0]
        self.powerStatus = 0
        self.battery1 = [0, 0]
        self.battery2 = [0, 0]
        
        #For SIB
        self.sibGuiData = [0, 0, 0]
        self.internalTemp1, self.internalTemp2, self.internalTemp3 = 0, 0, 0
        self.internalPressure1, self.internalPressure2, self.internalPressure3 = 0, 0, 0
        self.externalPressure1, self.externalPressure2, self.externalPressure3 = 0, 0, 0
        self.medianInternalTemp, self.medianInternalPressure, self.medianExternalDepth = 0, 0, 0
        
        #For HYDRAS
        self.heading1, self.aoi1, self.confidence1 = 0, 0, 0
        self.heading2, self.aoi2, self.confidence2 = 0, 0, 0
        self.hydrasPingerData = [[0, 0, 0], [0, 0, 0]]

        #For Joystick Controller
        self.joystickGuiData = [None]*9
        self.desiredMoveYaw, self.desiredMovePitch, self.desiredMoveRoll, self.desiredMoveDepth = 0, 0, 0, 0
        self.quickButtonPressYaw, self.quickButtonPressDepth, self.quickButtonPressOrientationLock = True, True, True
        self.toggleRightBumper = False
        self.setWaypoint = False
        self.removeWaypoint = False
        self.motorOffJoystickLock = True
        self.powerOnJoystickLock = False
        
        #For Missions
        self.currentMission = "None"
        self.powerOffMissionLock = True
        self.desiredMissionOrientation = [False, 0, 0, 0, 0]
        
        #Main process ready flag
        self.mainProccessReady = True #This flag will be set true every time the main process is ready to receive more data from pipe.send
        
    def start(self, pipe):
        '''
        Communicates with the boards to accept sensor feedback, control the Sub's movement, and communicates with the GUI.
        
        **Parameters**: \n
        * **pipe** - Child connection for Multiprocessing pipe.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        import Microcontrollers.microcontroller_sib, Microcontrollers.microcontroller_pmud, Microcontrollers.microcontroller_tcb, Microcontrollers.microcontroller_hydras
        import dvl
        import sparton_ahrs
        import joystick_controller
        import movement

        comPortList = pipe.recv() #First time a receive data from the pipe, its going to be com data
        print comPortList
        
        if useArduino:
            try:
                self.arduinoCom = serial.Serial("COM49", 9600)
            except:
                self.arduinoCom = serial.Serial(comPortList["AUX"], 9600)
                print "Arduino not Working!!!!!!!!!!"
        else:
            self.arduinoCom = serial.Serial(comPortList["WCB"], 9600)
        
        #Microcontroller initializing
        PMUDComPort = serial.Serial(comPortList["PMUD"], 9600)
        self.pmudDataPackets = microcontroller_pmud.PMUDDataPackets(PMUDComPort)
        self.pmudResponseThread = microcontroller_pmud.PMUDResponse(PMUDComPort)
        self.pmudDataPackets.setPowerStatus(1) #Turns dirty power on (ONLY UNCOMMENT FOR DEBUGGING PURPOSES ONLY)
        self.pmudResponseThread.start()
        
        DVLComPort = serial.Serial("COM41", 115200)
        self.dvlDataPackets = dvl.DVLDataPackets(DVLComPort)
        self.dvlResponseThread = dvl.DVLResponse(DVLComPort)
        self.dvlResponseThread.start()
        dvlAhrsComPort = serial.Serial("COM42", 38400)
        self.dvlAhrsDummyThread = dvl.AHRSDummyCommunicator(dvlAhrsComPort)
        self.dvlAhrsDummyThread.start()
        
        
        TCB1ComPort = serial.Serial(comPortList["TCB1"], 9600)
        self.tcb1DataPackets = microcontroller_tcb.TCBDataPackets(TCB1ComPort)
        self.tcb1ResponseThread = microcontroller_tcb.TCBResponse(TCB1ComPort)
        self.tcb1ResponseThread.start()
        
        TCB2ComPort = serial.Serial(comPortList["TCB2"], 9600)
        self.tcb2DataPackets = microcontroller_tcb.TCBDataPackets(TCB2ComPort)
        self.tcb2ResponseThread = microcontroller_tcb.TCBResponse(TCB2ComPort)
        self.tcb2ResponseThread.start()

        SIBComPort = serial.Serial(comPortList["SIB"], 9600)
        self.sibDataPackets = microcontroller_sib.SIBDataPackets(SIBComPort)
        self.sibResponseThread = microcontroller_sib.SIBResponse(SIBComPort)
        self.sibResponseThread.start()
        
        HYDRASComPort = serial.Serial(comPortList["HYDRAS"], 9600)
        self.hydrasDataPackets = microcontroller_hydras.HydrasDataPackets(HYDRASComPort)
        self.hydrasResponseThread = microcontroller_hydras.HydrasResponse(HYDRASComPort)
        self.hydrasResponseThread.start()
        
        
        
        #AHRS initializing
        self.spartonResponseThread1 = sparton_ahrs.SpartonAhrsResponse(comPortList["AHRS1"])
        self.spartonResponseThread1.start()
        self.spartonResponseThread2 = sparton_ahrs.SpartonAhrsResponse(comPortList["AHRS2"])
        self.spartonResponseThread2.start()
        self.spartonResponseThread3 = sparton_ahrs.SpartonAhrsResponse(comPortList["AHRS3"])
        self.spartonResponseThread3.start()
        
        #Controller Initalizing
        self.controllerResponseThread = joystick_controller.controllerResponse()
        self.controllerResponseThread.start()
        
        #Movement initializing
        thruster1, thruster2, thruster3, thruster4 = movement.BrushedThruster(1, [0, 1, 0], [1, 0, 1]), movement.BrushedThruster(2, [0, 1, 0], [-1, 0, 1]), movement.BrushedThruster(3, [0, 1, 0], [1, 0, -1]), movement.BrushedThruster(4, [0, 1, 0], [-1, 0, -1])   #Up/Down thruster
        thruster5, thruster6 = movement.BrushedThruster(5, [-1, 0, 0], [0, 1, 1]), movement.BrushedThruster(6, [-1, 0, 0], [0, 1, -1]) #Left/Right thruster
        thruster7, thruster8 = movement.BrushedThruster(7, [0, 0, -1], [1, 1, 0]), movement.BrushedThruster(8, [0, 0, -1], [-1, 1, 0]) #Fwd/Rev thruster
        self.moveController = movement.MovementController(self.tcb1DataPackets, self.tcb2DataPackets, thruster1, thruster2, thruster3, thruster4, thruster5, thruster6, thruster7, thruster8)
        self.joystickMoveController = movement.JoystickMovementController(self.tcb1DataPackets, self.tcb2DataPackets, thruster1, thruster2, thruster3, thruster4, thruster5, thruster6, thruster7, thruster8)
        
        while self.runProcess:
            #AHRS
            self.ahrsData1 = self.spartonAhrsData1()
            self.ahrsData2 = self.spartonAhrsData2()
            self.ahrsData3 = self.spartonAhrsData3()
            self.ahrsDataMedian = self.calculateMedianAhrs(self.ahrsData1, self.ahrsData2, self.ahrsData3)
            #self.ahrsDataMedian = [0, 0, 0]
            
            self.dvlAhrsDummyThread.updateAhrsValues(self.ahrsDataMedian)
            
            #JOYSTICK
            self.controllerResponseThread.updateManualControlMode(self.guiData[3])
            if self.guiData[3] == True: #Tells whether manual control is enabled or not (True = enabled)
                if self.powerOnJoystickLock == False: #Dont want to tell PMUD to turn power on multiple times when joystick control mode is activated
                    self.pmudDataPackets.setPowerStatus(1) #Turn dirty power on
                    self.powerOnJoystickLock = True
                self.joystickGuiData = self.controllerData(self.ahrsDataMedian)
                self.motorOffJoystickLock = False
                
            if self.guiData[3] == False and self.motorOffJoystickLock == False: #Dont want to tell TCB to constantly turn motors off when joystick control mode is deactivated
                self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
                self.joystickMoveController.previousPwm = [-1, -1, -1, -1, -1, -1, -1, -1] #Upon turning manual mode off, the up and down thrusters wouldnt got back on because the pwm lock would register that it was that same previous values, need this to make the values diffrent upon turning off manual control mode
                self.tcb1DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(2, 0, 1)
                self.tcb1DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(4, 0, 1)
                self.tcb2DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(2, 0, 1)
                self.tcb2DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(4, 0, 1)
                self.pmudDataPackets.setPowerStatus(0) #Turn dirty power off
                self.motorOffJoystickLock = True
                self.powerOnJoystickLock = False
             
            #MISSIONS
            if self.guiData[1] == True and self.powerStatus == 1 and self.guiData[3] == False: #If the GUI's "Start Vehicle" button is pushed and dirty power is on and manual control mode is off
                if self.clearDVLDataInitial == True:
                    self.dvlResponseThread.clearDistanceTraveled()
                    self.clearDVLDataInitial = False
                
                self.missions.updateMissions(copy.deepcopy(self.missionSelectorData), self.moveController, self.joystickMoveController, self.guiData[5], self.dvlGuiData, self.ahrsDataMedian, self.medianExternalDepth, self.arduinoCom) #Mission params from user, Image processing values, orientation data, depth from pressure transducers
                self.thrusterPWMs, self.currentMission, self.desiredMissionOrientation = self.missions.executeMissions()
                self.powerOffMissionLock = False
                
            
                
            if self.guiData[1] == False: #If user presses "Stop Vehicle"
                self.currentMission = "None"
                if self.powerOffMissionLock == False:
                    self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
                    self.desiredMissionOrientation = [False, 0, 0, 0, 0]
                    self.tcb1DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(2, 0, 1)
                    self.tcb1DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(4, 0, 1)
                    self.tcb2DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(2, 0, 1)
                    self.tcb2DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(4, 0, 1)
                    self.pmudDataPackets.setPowerStatus(0) #Turn dirty power off
                    self.powerOffMissionLock = True
                    
                      
            #DVL 
            self.dvlGuiData = self.dvlData(self.ahrsDataMedian) 
            #self.dvlGuiData = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0]]   
              
            #TCB 
            tcbData, tcbAlertData = self.tcbData()
            #tcbData, tcbAlertData = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], None
            #PMUD
            self.pmudGuiData = self.pmudData()
            #self.pmudGuiData = [0, [[0, 0], [0, 0]]]
            
            #SIB
            self.sibGuiData = self.sibData()  
            #self.sibGuiData = [0, 0, 0]   
            
            self.hydrasPingerData = self.hydrasData()
            #hydrasData = [[0, 0, 0], [0, 0, 0], [0, 0, 0, 0]]

            #SENDING/RECIEVING PIPE
            if self.guiData[0] == True: #If the main process is ready to receive more data, send more data
                pipe.send([self.sibGuiData, self.ahrsDataMedian, self.thrusterPWMs, self.joystickGuiData, self.pmudGuiData, self.dvlGuiData, self.currentMission, self.setWaypoint, self.removeWaypoint, self.desiredMissionOrientation])
                self.guiData[0] = False #In order to not overflow the main process buffer, I can only send data when the main process is ready. The main process will update self.guiData[0] to True when it is ready to receive more data
             
            if pipe.poll() == True: #If there is data to receive...(This thread would just be paused on pipe.recv() if I didn't put this if statement here)
                self.guiData = pipe.recv() #[mainProcessReadyFlag, window.startVehicle, turnOffDirtyPower, window.manualModeEnabled, missionSelectorData, imageProcValues, setWaypoint, removewaypoint, reset DVL]
                
                if self.guiData[2] == True: #If the GUI is terminated
                    self.dvlResponseThread.killThread(); self.dvlAhrsDummyThread.killThread(); self.pmudResponseThread.killThread(); 
                    self.tcb1ResponseThread.killThread(); self.tcb2ResponseThread.killThread(); self.sibResponseThread.killThread(); 
                    self.spartonResponseThread1.killThread(); self.spartonResponseThread2.killThread(); self.spartonResponseThread3.killThread()
                    self.hydrasResponseThread.killThread(); self.controllerResponseThread.killThread(); 
                    self.tcb1DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(2, 0, 1)
                    self.tcb1DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb1DataPackets.setMotorDirectionSpeed(4, 0, 1)
                    self.tcb2DataPackets.setMotorDirectionSpeed(1, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(2, 0, 1)
                    self.tcb2DataPackets.setMotorDirectionSpeed(3, 0, 1); self.tcb2DataPackets.setMotorDirectionSpeed(4, 0, 1)
                    self.pmudDataPackets.setPowerStatus(0) #Turn dirty power off
                    self.runProcess = False
                    
                if self.guiData[4] != None: #The missionSelectorData will always send a none if the user does not update the mission selector list or click the "start vehicle" button
                    self.missionSelectorData = self.guiData[4]
                    self.missions = mission_planner.missions() #Creates a new instance of missions if the missions selector data is changed
                if self.powerStatus == 0: #If the dirty power is killed, start the missions over again
                    self.missions = mission_planner.missions() #Creates a new instance of missions if the missions selector data is changed
                    self.clearDVLDataInitial = True
                if self.guiData[6] == True: #Turn off waypoints so that I only record waypoints one at a time
                    self.setWaypoint = False
                if self.guiData[7] == True:
                    self.removeWaypoint = False
                    
                if self.guiData[8] == True:
                    #dvl.reset or something
                    self.dvlResponseThread.clearDistanceTraveled()
                    
            sys.stdout.flush() #Allows me to print
    
            
    def dvlData(self, ahrsData):
        '''
        Communicates with the boards to accept sensor feedback, control the Sub's movement, and communicates with the GUI.
        
        **Parameters**: \n
        * **ahrsData** - Orientation data from the AHRS.
        
        **Returns**: \n
        * **[self.position, self.velocity, self.orientation, self.dvlMiscData]** - Position, velocity, orientation and other data detected by the DVL.\n
        '''
        while len(self.dvlResponseThread.getList) > 0:
            ensemble = self.dvlResponseThread.getList.pop(0)
            
            try:
                northPosition = (struct.unpack('i', struct.pack('I', ensemble[61] << 24 | ensemble[60] << 16 | ensemble[59] << 8 | ensemble[58]))[0])*0.00328084 #mm to feet
                eastPosition = (struct.unpack('i', struct.pack('I', ensemble[57] << 24 | ensemble[56] << 16 | ensemble[55] << 8 | ensemble[54]))[0])*0.00328084 #mm to feet
                upPosition = (struct.unpack('i', struct.pack('I', ensemble[65] << 24 | ensemble[64] << 16 | ensemble[63] << 8 | ensemble[62]))[0])*0.00328084 #mm to feet
                positionError = struct.unpack('i', struct.pack('I', ensemble[69] << 24 | ensemble[68] << 16 | ensemble[67] << 8 | ensemble[66]))[0]
                self.position = [northPosition, eastPosition, upPosition, positionError]
                
                xVel = (struct.unpack('h', struct.pack('H', ensemble[6] << 8 | ensemble[5]))[0])*0.00328084 #mm/s to feet/s
                yVel = (struct.unpack('h', struct.pack('H', ensemble[8] << 8 | ensemble[7]))[0])*0.00328084 #mm/s to feet/s
                zVel = (struct.unpack('h', struct.pack('H', ensemble[10] << 8 | ensemble[9]))[0])*0.00328084 #mm/s to feet/s
                self.velocity = [xVel, yVel, zVel] #East, North, Up
                
                heading = (ensemble[53] << 8 | ensemble[52])/100.0
                pitch = struct.unpack('h', struct.pack('H', ensemble[49] << 8 | ensemble[48]))[0]/100.0
                roll = struct.unpack('h', struct.pack('H', ensemble[51] << 8 | ensemble[50]))[0]/100.0
                depth = struct.unpack('h', struct.pack('H', ensemble[47] << 8 | ensemble[46]))[0]/100.0
                self.orientation = [heading, pitch, roll, depth]
                
                elevation = struct.unpack('h', struct.pack('H', ensemble[12] << 8 | ensemble[11]))[0]
                speedOfSound = struct.unpack('h', struct.pack('H', ensemble[42] << 8 | ensemble[41]))[0]
                waterTemp = struct.unpack('h', struct.pack('H', ensemble[44] << 8 | ensemble[43]))[0]/100.0 #deg c
                self.dvlMiscData = [elevation, speedOfSound, waterTemp]
                
            except:
                northPosition, eastPosition, upPosition, positionError = 0, 0, 0, 0
                xVel, yVel, zVel = 0, 0, 0
                heading, pitch, roll, depth = 0, 0, 0, 0
                elevation, speedOfSound, waterTemp = 0, 0, 0
                
            
            #print "Positions(ft) (North, East, Up, Error)", northPosition, eastPosition, upPosition, positionError
            #print "Velocities(ft/s) (X, Y, Z):", xVel, yVel, zVel
            #print "Yaw, Pitch, Roll, Depth (deg, deg, deg, m):", heading, pitch, roll, depth
            #print "Elevation Velocity, Speed Of Sound, Water Temp: (mm/s, m/s, deg C)", elevation, speedOfSound, waterTemp
            #print "\n"
            
        return [self.position, self.velocity, self.orientation, self.dvlMiscData]

    def spartonAhrsData1(self):
        '''
        Gets data from one of the AHRS.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **self.ahrsData1** - Latest AHRS orientation data.\n
        '''
        while len(self.spartonResponseThread1.getList) > 0:
            self.ahrsData1 = self.spartonResponseThread1.getList.pop(0)
        return self.ahrsData1
    
    def spartonAhrsData2(self):
        '''
        Gets data from one of the AHRS.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **self.ahrsData2** - Latest AHRS orientation data.\n
        '''
        while len(self.spartonResponseThread2.getList) > 0:
            self.ahrsData2 = self.spartonResponseThread2.getList.pop(0)
        return self.ahrsData2
    
    def spartonAhrsData3(self):
        '''
        Gets data from one of the AHRS.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **self.ahrsData3** - Latest AHRS orientation data.\n
        '''
        while len(self.spartonResponseThread3.getList) > 0:
            self.ahrsData3 = self.spartonResponseThread3.getList.pop(0)
        return self.ahrsData3
    
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
    
    
    def controllerData(self, ahrsData):
        '''
        Calculates the median values of the AHRS data to minimize error.
        
        **Parameters**: \n
        * **ahrsData** - Latest AHRS orientation data.
        
        **Returns**: \n
        * **self.joystickGuiData[0]** - String containing joystick's name.
        * **self.joystickGuiData[1]** - List of axis values.
        * **self.joystickGuiData[2]** - List of button values.
        * **self.joystickGuiData[3]** - List of hats values.
        * **self.toggleRightBumper** - Boolean which activates Orientation Lock when True.
        * **self.desiredMoveYaw** - Double between 0 and 360 indicating desired yaw.
        * **self.desiredMovePitch** - Double indicating desired pitch.
        * **self.desiredMoveRoll** - Double indicating desired roll.
        * **self.desiredMoveDepth** - Double at or below 0.0 indicating desired depth.\n
        '''
        while len(self.controllerResponseThread.getList) > 0:
            self.thrusterPWMs = [0, 0, 0, 0, 0, 0, 0, 0]
            self.joystickGuiData = self.controllerResponseThread.getList.pop(0)
            axis, buttons, hats = self.joystickGuiData[1], self.joystickGuiData[2], self.joystickGuiData[3]
            axis0, axis1, axis2, axis3, axis4 = int(axis[0]*204), int(axis[1]*204), int(axis[2]*204), int(axis[3]*204), int(axis[4]*204)
            #axis0:LJs-right/left, axis1:LJs-down/up, axis2:LRTrig-Left/Right, axis3:RJs-down/up, axis4:RJs-right/left

            #Waypoint
            if buttons[7] == True:
                self.setWaypoint = True
            if buttons[6] == True:
                self.removeWaypoint = True
                
            #WEAPONS ACTIVE
            if buttons[4] == True:
                if buttons[0] == True:
                    self.dropBall1()
                if buttons[1] == True:
                    self.dropBall2()
                if buttons[8] == True:
                    self.fireTorpedo1()
                if buttons[9] == True:
                    self.fireTorpedo2()
            
            #DEPTH
            if hats[0][1] != 0: #Have the ability to increment depth
                if self.quickButtonPressDepth == True: #Eliminates Schmitt trigger effect
                    self.desiredMoveDepth += -hats[0][1]*0.5
                    if self.desiredMoveDepth < 0:
                        self.desiredMoveDepth = 0.0
                    controllerDepthButtonReleaseTimer.restartTimer()
                    self.quickButtonPressDepth = False
                    #print self.desiredMoveDepth, "depth inc"
            elif hats[0][1] == 0:
                netControllerDepthButtonReleaseTimer = controllerDepthButtonReleaseTimer.netTimer(controllerDepthButtonReleaseTimer.cpuClockTimeInSeconds())
                if netControllerDepthButtonReleaseTimer >= 0.01: #Need to have let go of it for at least 10 miliseconds to register as button not being pressed
                    self.quickButtonPressDepth = True
                    controllerDepthButtonReleaseTimer.restartTimer()
  
            #TOGGLE ORIENTATION LOCK
            if buttons[5] == True:
                if self.quickButtonPressOrientationLock == True: #Eliminates Schmitt trigger effect
                    self.toggleRightBumper = not self.toggleRightBumper
                    self.quickButtonPressOrientationLock = False
            elif buttons[5] == False:
                self.quickButtonPressOrientationLock = True
                
            #ORIENTATION LOCK
            if self.toggleRightBumper == True: #Orientation lock
                poseData = [ahrsData[0], ahrsData[1], ahrsData[2], self.medianExternalDepth]
                self.thrusterPWMs = self.joystickMoveController.advancedMove(poseData, axis0, self.desiredMoveDepth, -axis1, self.desiredMovePitch, self.desiredMoveYaw, self.desiredMoveRoll) #By not updating the ahrs value, it allows the last values from the ahrs before the button was pushed to be my new baseline
                if hats[0][0] != 0: #Have the ability to increment yaw while orientation is locked
                    if self.quickButtonPressYaw == True: #Eliminates Schmitt trigger effect
                        self.desiredMoveYaw = ((self.desiredMoveYaw + hats[0][0]*5))%360
                        controllerYawButtonReleaseTimer.restartTimer()
                        self.quickButtonPressYaw = False
                        #print self.desiredMoveYaw, "yaw inc"
                elif hats[0][0] == 0:
                    netControllerYawButtonReleaseTimer = controllerYawButtonReleaseTimer.netTimer(controllerYawButtonReleaseTimer.cpuClockTimeInSeconds())
                    if netControllerYawButtonReleaseTimer >= 0.01: #Need to have let go of it for at least 10 miliseconds to register as button not being pressed
                        self.quickButtonPressYaw = True
                        controllerYawButtonReleaseTimer.restartTimer()
            
            #NORMAL OPERATION        
            elif self.toggleRightBumper == False:
                self.thrusterPWMs = self.joystickMoveController.move(self.medianExternalDepth, axis0, self.desiredMoveDepth, -axis1, axis3, axis4, -axis2)
                self.desiredMoveYaw, self.desiredMovePitch, self.desiredMoveRoll = ahrsData[0], ahrsData[1], ahrsData[2]
                   
        return self.joystickGuiData[0], self.joystickGuiData[1], self.joystickGuiData[2], self.joystickGuiData[3], self.toggleRightBumper, self.desiredMoveYaw, self.desiredMovePitch, self.desiredMoveRoll, self.desiredMoveDepth
        
    def pmudData(self):
        '''
        Gets data from the PMUDand shuts off the batteries if over 18 Amps are detected.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **self.powerStatus** - Power status.
        * **[self.battery1, self.battery2]** - Battery voltage and current data.\n
        '''
        while len(self.pmudResponseThread.getList) > 0:
            pmudGetDataPacket = self.pmudResponseThread.getList.pop(0)
            
            if pmudGetDataPacket[1] == 37:
                self.powerStatus = pmudGetDataPacket[2]
                
            if pmudGetDataPacket[1] == 38:
                self.battery1 = [round(((pmudGetDataPacket[3] << 8) | pmudGetDataPacket[2])*(102.4/65536.0), 2), round(((pmudGetDataPacket[5] << 8) | pmudGetDataPacket[4])*((0.1024/65536.0)/0.005), 2)]
                
            if pmudGetDataPacket[1] == 39:
                self.battery2 = [round(((pmudGetDataPacket[3] << 8) | pmudGetDataPacket[2])*(102.4/65536.0), 2), round(((pmudGetDataPacket[5] << 8) | pmudGetDataPacket[4])*((0.1024/65536.0)/0.005), 2)]
                
            if self.battery1[1] >= 18 or self.battery2[1] >= 18: #If greater than 15 amps
                self.pmudDataPackets.setPowerStatus(0)
                print "GREATER THAN 18A!!!"
                
        return self.powerStatus, [self.battery1, self.battery2]
            
    def tcbData(self):
        '''
        Sets thruster PWM and receives thruster feedback.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **[tcb1Data, tcb2Data]** - Thruster information such as updated PWM.
        * **[tcb1AlertData, tcb2AlertData]** - Thruster alert data.\n
        '''
        #TCB1
        while len(self.tcb1ResponseThread.getList) > 0: #While the TCB1 and TCB2 response threads have something in their buffer...
                
            tcb1GetDataPacket = self.tcb1ResponseThread.getList.pop(0) #Pop the data packet off of TCB1
            
            #This block of code is making the desired and actual direction be a positive or negative sign on the desired and actual pwm numbers
            if (tcb1GetDataPacket[1] == 1): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb1GetDataPacket[2] == 1:
                    self.tcb1Motor1Payload[0] = -1*tcb1GetDataPacket[4]
                else:
                    self.tcb1Motor1Payload[0] = tcb1GetDataPacket[4]
                
                if tcb1GetDataPacket[3] == 1:
                    self.tcb1Motor1Payload[1] = -1*tcb1GetDataPacket[5]
                else:
                    self.tcb1Motor1Payload[1] = tcb1GetDataPacket[5]
                    
                self.tcb1Motor1Payload[2] = (tcb1GetDataPacket[7] << 8) | tcb1GetDataPacket[6]
                
                #logger.logData("Motor 1",  "MC", 1, "Desired Direction:", self.motor1Payload[0], "Desired Speed:", self.motor1Payload[1], "Current Direction:", self.motor1Payload[2], "Current Speed:", self.motor1Payload[3])
                
            elif (tcb1GetDataPacket[1] == 2): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb1GetDataPacket[2] == 1:
                    self.tcb1Motor2Payload[0] = -1*tcb1GetDataPacket[4]
                else:
                    self.tcb1Motor2Payload[0] = tcb1GetDataPacket[4]
                
                if tcb1GetDataPacket[3] == 1:
                    self.tcb1Motor2Payload[1] = -1*tcb1GetDataPacket[5]
                else:
                    self.tcb1Motor2Payload[1] = tcb1GetDataPacket[5]
                    
                self.tcb1Motor2Payload[2] = (tcb1GetDataPacket[7] << 8) | tcb1GetDataPacket[6]
                
                #logger.logData("Motor 2", "MC", 2, "Desired Direction:", self.motor2Payload[0], "Desired Speed:", self.motor2Payload[1], "Current Direction:", self.motor2Payload[2], "Current Speed:", self.motor2Payload[3])
                
            elif (tcb1GetDataPacket[1] == 3): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb1GetDataPacket[2] == 1:
                    self.tcb1Motor3Payload[0] = -1*tcb1GetDataPacket[4]
                else:
                    self.tcb1Motor3Payload[0] = tcb1GetDataPacket[4]
                
                if tcb1GetDataPacket[3] == 1:
                    self.tcb1Motor3Payload[1] = -1*tcb1GetDataPacket[5]
                else:
                    self.tcb1Motor3Payload[1] = tcb1GetDataPacket[5]
                    
                self.tcb1Motor3Payload[2] = (tcb1GetDataPacket[7] << 8) | tcb1GetDataPacket[6]
                
                #logger.logData("Motor 3", "MC", 3, "Desired Direction:", self.motor3Payload[0], "Desired Speed:", self.motor3Payload[1], "Current Direction:", self.motor3Payload[2], "Current Speed:", self.motor3Payload[3])
                
            elif (tcb1GetDataPacket[1] == 4): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb1GetDataPacket[2] == 1:
                    self.tcb1Motor4Payload[0] = -1*tcb1GetDataPacket[4]
                else:
                    self.tcb1Motor4Payload[0] = tcb1GetDataPacket[4]
                
                if tcb1GetDataPacket[3] == 1:
                    self.tcb1Motor4Payload[1] = -1*tcb1GetDataPacket[5]
                else:
                    self.tcb1Motor4Payload[1] = tcb1GetDataPacket[5]
                    
                self.tcb1Motor4Payload[2] = (tcb1GetDataPacket[7] << 8) | tcb1GetDataPacket[6]
                
                #logger.logData("Motor 4", "MC", 4, "Desired Direction:", self.motor4Payload[0], "Desired Speed:", self.motor4Payload[1], "Current Direction:", self.motor4Payload[2], "Current Speed:", self.motor4Payload[3])
                
        while len(self.tcb1ResponseThread.alertList) > 0:
            tcb1AlertData = self.tcb1ResponseThread.alertList.pop(0)
            #Could do actions under here according to what data packet is and only return the important stuff to reduce overhead
        
        #Desired Direction & PWM, Actual Direction & PWM, Hall Effect Sensor
        tcb1Data = [[self.tcb1Motor1Payload[0], self.tcb1Motor1Payload[1], self.tcb1Motor1Payload[2]],
                    [self.tcb1Motor2Payload[0], self.tcb1Motor2Payload[1], self.tcb1Motor2Payload[2]],
                    [self.tcb1Motor3Payload[0], self.tcb1Motor3Payload[1], self.tcb1Motor3Payload[2]],
                    [self.tcb1Motor4Payload[0], self.tcb1Motor4Payload[1], self.tcb1Motor4Payload[2]]]
           
        tcb1AlertData = None
                

 
        #TCB2   
        while len(self.tcb2ResponseThread.getList) > 0:
            
            tcb2GetDataPacket = self.tcb2ResponseThread.getList.pop(0) #Pop the data packet off of TCB1
            
            #This block of code is making the desired and actual direction be a positive or negative sign on the desired and actual pwm numbers
            if (tcb2GetDataPacket[1] == 1): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb2GetDataPacket[2] == 1:
                    self.tcb2Motor1Payload[0] = -1*tcb2GetDataPacket[4]
                else:
                    self.tcb2Motor1Payload[0] = tcb2GetDataPacket[4]
                
                if tcb2GetDataPacket[3] == 1:
                    self.tcb2Motor1Payload[1] = -1*tcb2GetDataPacket[5]
                else:
                    self.tcb2Motor1Payload[1] = tcb2GetDataPacket[5]
                    
                self.tcb2Motor1Payload[2] = (tcb2GetDataPacket[7] << 8) | tcb2GetDataPacket[6]
                
                #logger.logData("Motor 1",  "MC", 1, "Desired Direction:", self.motor1Payload[0], "Desired Speed:", self.motor1Payload[1], "Current Direction:", self.motor1Payload[2], "Current Speed:", self.motor1Payload[3])
                
            elif (tcb2GetDataPacket[1] == 2): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb2GetDataPacket[2] == 1:
                    self.tcb2Motor2Payload[0] = -1*tcb2GetDataPacket[4]
                else:
                    self.tcb2Motor2Payload[0] = tcb2GetDataPacket[4]
                
                if tcb2GetDataPacket[3] == 1:
                    self.tcb2Motor2Payload[1] = -1*tcb2GetDataPacket[5]
                else:
                    self.tcb2Motor2Payload[1] = tcb2GetDataPacket[5]
                    
                self.tcb2Motor2Payload[2] = (tcb2GetDataPacket[7] << 8) | tcb2GetDataPacket[6]
                
                #logger.logData("Motor 2", "MC", 2, "Desired Direction:", self.motor2Payload[0], "Desired Speed:", self.motor2Payload[1], "Current Direction:", self.motor2Payload[2], "Current Speed:", self.motor2Payload[3])
                
            elif (tcb2GetDataPacket[1] == 3): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb2GetDataPacket[2] == 1:
                    self.tcb2Motor3Payload[0] = -1*tcb2GetDataPacket[4]
                else:
                    self.tcb2Motor3Payload[0] = tcb2GetDataPacket[4]
                
                if tcb2GetDataPacket[3] == 1:
                    self.tcb2Motor3Payload[1] = -1*tcb2GetDataPacket[5]
                else:
                    self.tcb2Motor3Payload[1] = tcb2GetDataPacket[5]
                    
                self.tcb2Motor3Payload[2] = (tcb2GetDataPacket[7] << 8) | tcb2GetDataPacket[6]
                
                #logger.logData("Motor 3", "MC", 3, "Desired Direction:", self.motor3Payload[0], "Desired Speed:", self.motor3Payload[1], "Current Direction:", self.motor3Payload[2], "Current Speed:", self.motor3Payload[3])
                
            elif (tcb2GetDataPacket[1] == 4): #Desired Direction, Actual Direction, Desired PWM, Actual PWM, Hall Effect Sensor
                if tcb2GetDataPacket[2] == 1:
                    self.tcb2Motor4Payload[0] = -1*tcb2GetDataPacket[4]
                else:
                    self.tcb2Motor4Payload[0] = tcb2GetDataPacket[4]
                
                if tcb2GetDataPacket[3] == 1:
                    self.tcb2Motor4Payload[1] = -1*tcb2GetDataPacket[5]
                else:
                    self.tcb2Motor4Payload[1] = tcb2GetDataPacket[5]
                    
                self.tcb2Motor4Payload[2] = (tcb2GetDataPacket[7] << 8) | tcb2GetDataPacket[6]
                
                #logger.logData("Motor 4", "MC", 4, "Desired Direction:", self.motor4Payload[0], "Desired Speed:", self.motor4Payload[1], "Current Direction:", self.motor4Payload[2], "Current Speed:", self.motor4Payload[3])
                
        while len(self.tcb1ResponseThread.alertList) > 0:
            tcb2AlertData = self.tcb1ResponseThread.alertList.pop(0)
            #Could do actions under here according to what data packet is and only return the important stuff to reduce overhead
        
        #Desired Direction & PWM, Actual Direction & PWM, Hall Effect Sensor
        tcb2Data = [[self.tcb2Motor1Payload[0], self.tcb2Motor1Payload[1], self.tcb2Motor1Payload[2]],
                    [self.tcb2Motor2Payload[0], self.tcb2Motor2Payload[1], self.tcb2Motor2Payload[2]],
                    [self.tcb2Motor3Payload[0], self.tcb2Motor3Payload[1], self.tcb2Motor3Payload[2]],
                    [self.tcb2Motor4Payload[0], self.tcb2Motor4Payload[1], self.tcb2Motor4Payload[2]]]
           
        tcb2AlertData = None
        
        
        return [tcb1Data, tcb2Data], [tcb1AlertData, tcb2AlertData]
    
    def sibData(self):
        '''
        Gets data on internal temperature, internal pressure, and external pressure.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **[round(self.medianInternalTemp, 2), round(self.medianInternalPressure, 2), round(self.medianExternalDepth, 2)]** - Internal temperature, internal pressure, and external pressure data.\n
        '''
        while len(self.sibResponseThread.getList) > 0:
            sibGetDataPacket = self.sibResponseThread.getList.pop(0)
            
            if sibGetDataPacket[1] == 109:
                self.internalTemp1 = 1.0/((math.log((10000.0/((1023.0 / (sibGetDataPacket[3] << 8 | sibGetDataPacket[2])) - 1))/10000.0)/3630.0) + (1/(25.0+273.15))) - 253.15
                self.internalTemp2 = 1.0/((math.log((10000.0/((1023.0 / (sibGetDataPacket[5] << 8 | sibGetDataPacket[4])) - 1))/10000.0)/3630.0) + (1/(25.0+273.15))) - 253.15
                self.internalTemp3 = 1.0/((math.log((10000.0/((1023.0 / (sibGetDataPacket[7] << 8 | sibGetDataPacket[6])) - 1))/10000.0)/3630.0) + (1/(25.0+273.15))) - 253.15
                #print self.internalTemp1, self.internalTemp2, self.internalTemp3
                self.medianInternalTemp = numpy.median(numpy.array([self.internalTemp1, self.internalTemp2, self.internalTemp3]))
                
            elif sibGetDataPacket[1] == 110:
                self.internalPressure1 = sibGetDataPacket[3] << 8 | sibGetDataPacket[2]
                self.internalPressure2 = sibGetDataPacket[5] << 8 | sibGetDataPacket[4]
                self.internalPressure3 = sibGetDataPacket[7] << 8 | sibGetDataPacket[6]
                #print "Internal Pressure:", self.internalPressure1, self.internalPressure2, self.internalPressure3
                self.medianInternalPressure = numpy.median(numpy.array([self.internalPressure1, self.internalPressure2, self.internalPressure3]))
                
            elif sibGetDataPacket[1] == 111:
                #73.0
                self.externalPressure1 = ((((sibGetDataPacket[3] << 8 | sibGetDataPacket[2])*71.0)/1023)-14.7)/0.4335 #Aquaplex: 84.0/my house:71.2/Sonias: 76.8
                self.externalPressure2 = ((((sibGetDataPacket[5] << 8 | sibGetDataPacket[4])*71.0)/1023)-14.7)/0.4335
                self.externalPressure3 = ((((sibGetDataPacket[7] << 8 | sibGetDataPacket[6])*71.0)/1023)-14.7)/0.4335
                #print "External Pressure:", self.externalPressure1, self.externalPressure2, self.externalPressure3
                self.medianExternalDepth = numpy.median(numpy.array([self.externalPressure1, self.externalPressure2, self.externalPressure3]))#((((numpy.median(numpy.array([self.externalPressure1, self.externalPressure2, self.externalPressure3])))*46.3)/1023)-14.7)/0.43 #Depth under water in feet
            
            

            #print [self.medianInternalTemp, self.medianInternalPressure, self.medianExternalDepth], [self.internalTemp1, self.internalTemp2, self.internalTemp3], [self.internalPressure1, self.internalPressure2, self.internalPressure3], [self.externalPressure1, self.externalPressure2, self.externalPressure3]

        return [round(self.medianInternalTemp, 2), round(self.medianInternalPressure, 2), round(self.medianExternalDepth, 2)]
    
    def hydrasData(self):
        '''
        Gets data on pinger location
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **[[self.heading1, self.aoi1, self.confidence1], [self.heading2, self.aoi2, self.confidence2]]** - Heading, area of interest, and confidence values for both pingers.\n
        '''
        while len(self.hydrasResponseThread.getList) > 0:
            hydrasGetDataPacket = self.hydrasResponseThread.getList.pop(0)
            
            if hydrasGetDataPacket[1] == 96:
                self.heading1 = hydrasGetDataPacket[3] << 8 | hydrasGetDataPacket[2]
                self.aoi1 = hydrasGetDataPacket[5] << 8 | hydrasGetDataPacket[4]
                self.confidence1 = hydrasGetDataPacket[6]
                
            elif hydrasGetDataPacket[1] == 97:
                self.heading2 = hydrasGetDataPacket[3] << 8 | hydrasGetDataPacket[2]
                self.aoi2 = hydrasGetDataPacket[5] << 8 | hydrasGetDataPacket[4]
                self.confidence2 = hydrasGetDataPacket[6]
                
            print [[self.heading1, self.aoi1, self.confidence1], [self.heading2, self.aoi2, self.confidence2]]
                
        return [[self.heading1, self.aoi1, self.confidence1], [self.heading2, self.aoi2, self.confidence2]]
                
                
        
    def __logNavigationData__(self, **kwargs): #Might not need to have this hear. Could have this in the main since this data will be sent there anyway
        '''
        Slows down the rate to not log values faster than they are updated.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Returns**: \n
        * **No Return.**\n
        '''
        if self.loggerIterationCounter >= 4:
            #logger.logData('Position', kwargs.get('position')[0], kwargs.get('position')[1], kwargs.get('position')[2])
            #logger.logData('Yaw', kwargs.get('yaw'))
            #logger.logData('Pitch', kwargs.get('pitch'))
            #logger.logData('Roll', kwargs.get('roll'))
            self.loggerIterationCounter = 0
        self.loggerIterationCounter += 1
        
    def dropBall1(self):        
        self.arduinoCom.write("ball1")
    
    def dropBall2(self):
        self.arduinoCom.write("ball2")
    
    def fireTorpedo1(self):
        self.arduinoCom.write("torpedo1")
    
    def fireTorpedo2(self):
        self.arduinoCom.write("torpedo2")
        