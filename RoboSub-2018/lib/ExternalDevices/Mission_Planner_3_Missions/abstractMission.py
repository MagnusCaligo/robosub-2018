from PyQt4 import QtCore, QtGui
import math
'''
This is class contains the abstraction of a mission
All missions will look something like this
'''


class AbstractMission(QtCore.QObject):
	
    #Default parameters to be displayed in the Mission Commander
    defaultParameters = "waitTime = 10\nuseRelativeWaypoint = False\nuseRelativeWorld = False\n"
	
    def __init__(self, parameters):
        QtCore.QObject.__init__(self)
        self.generalWaypoint = [0,0,0,0,0,0] #This is the value that is inputted, might change during runtime
        self.finalWaypoint = [0,0,0,0,0,0] #This is the final value of the waypoint after it has been modified
        self.name = parameters["name"]
        self.parameters = {}
        
        self.generalDistanceError = 1
        self.generalRotationError = 6
        
        
        self.waypointError = None
        self.startTime = None

        self.position = [0,0,0]
        self.orientation = [0,0,0]

        self.cameraMatrix = [[808, 0, 404],
                            [0,608,304],
                            [0,0,1.0]]

        '''
        Key values inside of parameters
        name - The name of the mission
        maxTime - the maximum time for the mission
        missionType - What type of mission it is; saved as a string and in the same format as
        DirectionToLook - This is the direction we will look for obstacles, either a -1 for c
        useWaypoint - This value is defaulted at 0... if the user wants to set this mission's
        waypoint, then this value will be the name of that waypoint. This val
        useKalmanFilter - This value is defaulted to True, but can be set to false to use pur
        parametersString - This has a bunch of parameters in them in the form of a string tak
        useLaser - Boolean which defines if we will be using the laser or not for the mission
        drivingMode - Whether the sub moves forward or backwards. 0 for forward 1 for backwar
        useRelativeWaypoint - whether the general waypoint is just a relative waypoint, defau
        useRelativeWorld - use relative movement but relative north, east, and up rather than
        '''

        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 1
        self.parameters["drivingMode"] = 0
        self.parameters["useRelativeWaypoint"] = "False"
        self.parameters["useRelativeWorld"] = "False"

        for i,v in parameters.iteritems():
            self.parameters[i] = v

    def useFrontCamera(self):
	self.emit(QtCore.SIGNAL("useFrontCamera"))

    def useBottomCamera(self):
	self.emit(QtCore.SIGNAL("useBottomCamera"))

    def fireTorpedo1(self):
	self.emit(QtCore.SIGNAL("fireTorpedo1"))

    def updateDetectionData(self, detections):
        self.detectionData = detections

    def updateLocation(self, position, orientation):
        self.position = position
        self.orientation = orientation
        
    def update(self):
        pass
    
    def initalizeOnMissionStart(self):
	self.useFrontCamera()
        #If we are using relative waypoints we need to adjust them only when the mission is starting
        if self.parameters["useRelativeWaypoint"] in ["True", 'true']: #If we are using relativeWaypoint we need to modify the waypoint based on our current position
			
            pose, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, self.generalWaypoint[1],self.generalWaypoint[2],self.generalWaypoint[0],
				self.generalWaypoint[3],self.generalWaypoint[4],self.generalWaypoint[5])

            self.finalWaypoint = [n,e,u,y,0,0]
			
            self.writeDebugMessage("Waypoint is " + str(self.finalWaypoint))

        elif self.parameters["useRelativeWorld"] in ["True", 'true']:
            pose, n, e, u, p, y, r = self.movementController.relativeMoveNEU(self.orientation + self.position, self.generalWaypoint[0],self.generalWaypoint[1],self.generalWaypoint[2],
				self.generalWaypoint[3],self.generalWaypoint[4],self.generalWaypoint[5])

            self.finalWaypoint = [n,e,u, y,0,0]
            self.writeDebugMessage("Waypoint is " + str(self.finalWaypoint))
        else:
            self.finalWaypoint = self.generalWaypoint #If not using any relativity, then we can assume that the waypoint is absolute coordinate

    

    def setMovementController(self, movementController):
        self.movementController = movementController
        
    def writeDebugMessage(self, string):
        self.emit(QtCore.SIGNAL("debugMessage(PyQt_PyObject)"), string)

    def moveToWaypoint(self, waypoint, lockOrientation=False):
	print "WAYPOINT IS", waypoint, "======"
        self.waypointError = self.movementController.advancedMove(self.orientation+self.position, waypoint[0], waypoint[1], waypoint[2], 
                      waypoint[4], waypoint[3], waypoint[5], lockOrientation=lockOrientation)[1]
	#print "Waypoint Error:", self.waypointError
        
        reachedWaypoint = True #Assume we reached the waypoint, check the math to see if we are within the error
        if abs(self.waypointError[0]) < self.generalDistanceError and abs(self.waypointError[1]) < self.generalDistanceError + 5 and abs(self.waypointError[2]) < self.generalDistanceError:
            pass #This will only be called if we are actually at the waypoint in terms of position
        else:
            reachedWaypoint = False
            
        if abs(self.waypointError[3]) < self.generalRotationError and abs(self.waypointError[4]) < self.generalRotationError and abs(self.waypointError[5]) < self.generalRotationError:
            pass #Only will be called if we have the correct orientaiton
            #print "Not there orientation"
        else:
            reachedWaypoint = False
        return reachedWaypoint


