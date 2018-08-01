from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class DiceMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "dice# = 0\ngetDistanceAway = 2\nminimumEstimates=10\nmaxEstimates=100"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

    def initalizeOnMissionStart(self):
        AbstractMission.initalizeOnMissionStart(self)
            
        self.reachedFinalWaypoint = False
        self.detectionData = None
        self.lastKnownDepth = self.finalWaypoint[2]
	self.calculatedWaypoint = None

        self.foundObstacles = False
        self.diceClassNumber = int(self.parameters["dice#"])
	self.maxPositionEstimates= 25
        self.positionEstimates = []

        self.sentMessage1 = False
        self.sentMessage2 = False
        self.sentMessage3 = False
        self.sentMessage4 = False
        self.sentMessage5 = False
        
        self.hitBuoy = False
        self.movingForward = True
        self.inFrontOfBuoy = False
	self.linedUpWithBuoy = False
	self.calculatedLineUp = False

        self.atBuoyTimer = None
        self.lookingForObstaclesTimer = None
        self.hitBuoyTimer = None
        
        self.rotateTimer = None
        self.rotateWaitTime = 5

        self.depthAtRelativeMove = None
        self.lookingMaxTime = 10
        self.hitBuoyMaxTime = 5

        self.lookingAngle = 0
        self.lookingDifference = 20

        self.src_pts = [(-.4,-.4,0),(.4,-.4,0),(.4,.4,0),(-.4,.4,0)]


    def checkIfFoundObstacles(self):
        if self.detectionData == None:
            return False
        for i,v in enumerate(self.detectionData):
            if v[0] == int(self.parameters["dice#"]):
		#if v[1] >= 808 /3.0 and v[1] <=2 * 808 / 3.0:
		    return True
		#else:
		    #print "Found obstacle, but its not centered"
		    #print v[1] >= 808 /3.0, v[i] <= 2 * 808/3.0, v[i]
        return False

    def update(self):
        if not self.reachedFinalWaypoint and not self.checkIfFoundObstacles():
            self.reachedFinalWaypoint = self.moveToWaypoint(self.finalWaypoint)
            return -1
        else:
            self.reachedFinalWaypoint = True

        if self.reachedFinalWaypoint and not self.checkIfFoundObstacles() and len(self.positionEstimates) == 0:
            print "At waypoint, looking for obstacle"
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.finalWaypoint[2] -self.position[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,self.finalWaypoint[2],yaw,0,0]
	    print "Moving to waypoint:", self.calculatedWaypoint
            self.moveToWaypoint(self.calculatedWaypoint);
            if self.checkIfFoundObstacles() == True:
                self.foundObstacles = True
            return -1
        
        for det in [detection for detection in self.detectionData if detection[0] == int(self.parameters["dice#"])]:
	    if det[1] < 2 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
		poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, 0, 0, 0,-10,0,0)
		waypoint = [north,east,self.finalWaypoint[2],yaw,0,0]
		self.moveToWaypoint(waypoint)
		return -1
	    elif det[1] > 3 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
		poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, 0, 0, 0,10,0,0)
		waypoint = [north,east,self.finalWaypoint[2],yaw,0,0]
		self.moveToWaypoint(waypoint)
		return -1
            imgPoints = [(det[1] - (.5 * det[3]), det[2] - (.5* det[4])),(det[1] + (.5 * det[3]), det[2] - (.5* det[4])),
                         (det[1] + (.5 * det[3]), det[2] + (.5* det[4])),(det[1] - (.5 * det[3]), det[2] + (.5* det[4]))]
            rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(imgPoints).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
            poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0], -tvec[2][0],0,0,0)
	    if tvec[2][0] - .5< float(self.parameters["getDistanceAway"]):
		self.inFrontOfBuoy = True
	    print "Data:", tvec, north, east
            self.positionEstimates.append([north/1.0, east/1.0, up + .5, 0, 0,0])

	while len(self.positionEstimates) > self.maxPositionEstimates:
		self.positionEstimates.pop(0)
	print "Number of estimates", len(self.positionEstimates)

        #Hold position while getting data points
        if len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
	    print "See dice, holding position"
	    if self.calculatedWaypoint == None:
		self.calculatedWaypoint = self.finalWaypoint
            self.moveToWaypoint(self.calculatedWaypoint)
        #Else if we have enough points start moving to the obstacle
        elif len(self.positionEstimates) >= int(self.parameters["minimumEstimates"]) and not self.inFrontOfBuoy:
	    print "Got enough points, moving to detection"
            northEstimate = np.median(np.array([p[0] for p in self.positionEstimates]))
            eastEstimate = np.median(np.array([p[1] for p in self.positionEstimates]))
            upEstimate = np.median(np.array([p[2] for p in self.positionEstimates]))
            
            position = [northEstimate, eastEstimate, upEstimate]
            rotationDifference = math.degrees(math.atan2(position[1] - self.finalWaypoint[1], position[0] - self.finalWaypoint[0]))
            poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+position, 0, 0, int(self.parameters["getDistanceAway"]),0,0,0)
	    for det in [detection for detection in self.detectionData if detection[0] == int(self.parameters["dice#"])]:
	        if det[1] < 2 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
			rotationDifference = -10 + self.orientation[0]
	        elif det[1] > 3 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
			rotationDifference = 10 + self.orientation[0]
            self.calculatedWaypoint = [north, east, up, rotationDifference, 0, 0]
	    print "Going to waypoint", self.calculatedWaypoint
            self.inFrontOfBuoy = self.moveToWaypoint(self.calculatedWaypoint)
            
        elif self.inFrontOfBuoy:
	    if self.linedUpWithBuoy == False:
		print "Lining up with buoy"
		if len([detection for detection in self.detectionData if detection[0] == int(self.parameters["dice#"])]) == 0:
			print "Lost detection"
			self.inFrontOfBuoy = False
			self.positionEstimates = []
			self.foundObstacles = False
	        for det in [detection for detection in self.detectionData if detection[0] == int(self.parameters["dice#"])]:
	            if det[1] < 2 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
		    	rotationDifference = -10 + self.orientation[0]
		    	self.calculatedWaypoint[3] = rotationDifference	
			self.moveToWaypoint(self.calculatedWaypoint)
			return -1
	            elif det[1] > 3 * 808 / 5.0 and len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
			rotationDifference = 10 + self.orientation[0]
			self.calculatedWaypoint[3] = rotationDifference	
			self.moveToWaypoint(self.calculatedWaypoint)
			return -1
		    else:
			self.linedUpWithBuoy = True
			print "Lining up with buoy..."
			return -1
	
		    
            print "Trying to hit buoy"
            if self.hitBuoyTimer == None:
                self.hitBuoyTimer = time.time()
                self.writeDebugMessage("Moving Forward...")
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0, 0, -abs(int(self.parameters["getDistanceAway"]))-2, 0, 0, 0)
                self.diceWaypoint = [n,e,u,y,0,0]
            if time.time() - self.hitBuoyTimer >= self.hitBuoyMaxTime:
                if self.movingForward == False:
                    return 1 #Finished the mission
                self.movingForward = False
                self.writeDebugMessage("Moving Backward...")
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0.5, self.position[2] - self.depthAtRelativeMove, 2*abs(int(self.parameters["getDistanceAway"])), 0, 0, 0)
                self.diceWaypoint = [n,e,u,y,0,0]
                self.hitBuoyTimer = time.time()
            if self.depthAtRelativeMove == None:
                self.depthAtRelativeMove = self.position[2]
            #self.movementController.advancedMove(poseData, north, east, up, 0, yaw, 0)
            self.moveToWaypoint(self.diceWaypoint, lockOrientation=True)
            
        
        
        
