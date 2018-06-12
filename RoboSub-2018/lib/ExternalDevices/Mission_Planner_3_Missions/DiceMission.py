from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class DiceMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "dice# = 0\ngetDistanceAway = 2\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
        
	self.atWaypoint = False
        self.detectionData = None

        self.foundObstacles = False
        self.diceClassNumber = 0

        self.sentMessage1 = False
        self.sentMessage2 = False
        self.sentMessage3 = False
	self.sentMessage4 = False
	self.sentMessage5 = False
	
	self.hitBuoy = False
	self.movingForward = True

	self.atBuoyTimer = None
	self.lookingForObstaclesTimer = None
	self.hitBuoyTimer = None

	self.depthAtRelativeMove = None
	self.lookingMaxTime = 8
	self.hitBuoyMaxTime = 5

	self.lookingAngle = 0
	self.lookingDifference = 45

        self.src_pts = [(0,0,0),(.58,0,0),(.58,.58,0),(0,.58,0)]


    def checkIfFoundObstacles(self):
	if not 'classNumbers' in self.detectionData:
		return False
        for i,v in enumerate(self.detectionData['classNumbers']):
            if v == self.diceClassNumber:
                return True
        return False

    def sortThroughDetections(self):
	if not 'classNumbers' in self.detectionData:
		return None
        detections = []
        if self.detectionData != None:
            for i,v in enumerate(self.detectionData['classNumbers']):
                if v == self.diceClassNumber:
			detections.append([self.detectionData["classNumbers"][i], self.detectionData["xLocations"][i],self.detectionData["yLocations"][i],self.detectionData["widths"][i],self.detectionData["heights"][i]])
            return detections
        else:
            return None

    def update(self):
        #Approach General Waypoint
        if self.atWaypoint == False:
            atWaypoint = self.moveToWaypoint(self.finalWaypoint)
            if atWaypoint:
                if self.sentMessage1 == False:
                    self.writeDebugMessage("At Waypoint")
                    self.sentMessage1 = True
                    self.atWaypoint = True
            else:
                self.atWaypoint = False
                self.sentMessage1 = False
                self.atWaypointStartTime = None
                print "Not there"
                return -1
        
        #Look For obstacles
	if self.hitBuoy == False:
		if self.atWaypoint == True:
		    if not self.checkIfFoundObstacles():
			self.sentMessage3 = False
			if self.sentMessage2 == False:
			    self.writeDebugMessage("Couldn't Find Obstacles")
			    self.sentMessage2 = True
			if self.lookingForObstaclesTimer == None:
				self.lookingForObstaclesTimer = time.time()
				self.lookingAngle += self.lookingDifference
				print "Incrementing Angle"
			if time.time() - self.lookingForObstaclesTimer >= self.lookingMaxTime:
				self.lookingForObstaclesTimer = None
			waypoint = self.position + self.orientation
			waypoint[3] += self.lookingAngle
			print "Looking waypoint is", waypoint
			self.moveToWaypoint(waypoint)
		    else:
			self.sentMessage2 = False
			if self.sentMessage3 == False:
			    self.writeDebugMessage("Found Obstacles!")
			    self.sentMessage3 = True

			detections = self.sortThroughDetections()
			detection = detections[0] #We only need one detection so we assume that its the first one


			#These are the image points of the buoy in the image, this will be with the source points to get buoy depth
			img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]

			#Fake camera matrix
			cameraMatrix = [[808,     0, 404],
						[   0, 608, 304],
						[   0,     0,  1.0],]


			#Solve PNP returns the rotation vector and translation vector of the object
			rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
			
			center = detection[1] + (detection[3]/2)
			
			rotationDifference = math.degrees(math.atan2(tvec[0], tvec[2]))
	    
			if tvec[1] - int(self.parameters["getDistanceAway"]) < 1:
				self.atBuoyLocation = True
				if self.sentMessage4 == False:
					self.writeDebugMessage("Found Buoy")
					self.sentMessage4 = True
					self.sentMessage5 =  False
				if self.atBuoyTimer == None:
					self.atBuoyTimer = time.time()
				if time.time() - self.atBuoyTimer > float(self.parameters["waitTime"]):
					self.hitBuoy = True
			else:
				if self.sentMessage5 == False:
					self.writeDebugMessage("Not at Buoy Location")
					self.sentMessage5 = True
					self.sentMessage4 = False

	    
			#print "Distance: ", self.parameters["getDistanceAway"]
			poseData, north, east, up, yaw, pitch, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0], tvec[2][0]- int(self.parameters["getDistanceAway"]),0,0,0)

	elif self.hitBuoy == True:
		if self.hitBuoyTimer == None:
			self.hitBuoyTimer = time.time()
		if time.time() - self.hitBuoyTimer >= self.hitBuoyMaxTime:
			if self.movingForward == False:
				return 1 #Finished the mission
			self.movingForward = False
			self.hitBuoyTimer = time.time()
		distance = 1
		if not self.movingForward:
			distance = -1
		if self.depthAtRelativeMove == None:
			self.depthAtRelativeMove = self.position[2]
		self.movementController.relativeMoveXYZ(self.orientation + self.position, 0, self.position[2] - self.depthAtRelativeMove, distance, 0, 0, 0)



