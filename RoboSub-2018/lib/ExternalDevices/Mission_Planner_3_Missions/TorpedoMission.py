from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class TorpedoMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "xOffset=2\ndepthOffset=7\ngetDistanceAway = 2\nnumOfTries=1\nminimumEstimatesRequired=200\npullArm=True\ntorpedoThreshold = 60"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
	
        #Top Left, Top Right, Full Board, Bottom Hole, Cherry, Grape, Banana, Corner
        #self.classNumbers = [7, 8, 6,9,3,4,5,13]
        self.classNumbers = [8,9,10,11,12]
	self.fruitClassNumbers = []#[8,9,10]
        self.torpedoHoleClassNumber = 12
        self.minimumToSee = 1


    def initalizeOnMissionStart(self):
        AbstractMission.initalizeOnMissionStart(self)

        self.estimatedPoints = []
        self.estimatedTorpedoLocation = []

        self.calculatedWaypoint = None
        self.armWaypoint = None

	#Data Handling Algorithm2:
	self.SAMPLE_DATA = [];
        
    
        #Flags
        self.reachedFinalWaypoint = False
        self.foundObstacles = False
        self.reachedBoard = False
        self.pulledArm = False
        self.aboveArm = False
        self.finishedPulling = False
	self.timesAttempted = 0
	self.calculatedMoveDown = False
	self.fireTorpedo = True
	self.firedAt = None

        self.srcPoints = []
        self.imgPoints = []
        
        #Algorithm Stuff
        self.algorithm1Data = np.array([])
        
        #Timing stuff
        self.rotateTimer = None
        self.rotateWaitTime = None
        self.waitTimer = None
        self.waitTime = 10
        self.waitArmPullTimer = None
        self.armPullTime = 10

    def checkIfSeeObstacles(self):
        numWeSee = 0
        for detection in self.detectionData:
            if detection[0] in self.classNumbers:
                numWeSee += 1
        if numWeSee >= self.minimumToSee:
            return True
        return False
    


    def update(self):
	'''
        if not self.pulledArm:
            self.pullArmFromCurrentLocation()
            return -1
        else:
            return 1
	'''
        #Move to waypoint or move on if you see the board
        if not self.reachedFinalWaypoint and not self.checkIfSeeObstacles():
            self.reachedFinalWaypoint = self.moveToWaypoint(self.finalWaypoint)
	    print "Moving to waypoint"
            return -1
        else:
            self.reachedFinalWaypoint = True

        if self.reachedFinalWaypoint and not self.foundObstacles:
            print "At waypoint, looking for obstacle"
            if self.checkIfSeeObstacles() == True:
		print "Should have found obstacles"
                self.foundObstacles = True
		return -1
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.finalWaypoint[2] -self.position[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,self.finalWaypoint[2],yaw,0,0]
                print "Depth is", self.finalWaypoint[2]
            self.moveToWaypoint(self.calculatedWaypoint);
            return -1
            
        if len(self.estimatedPoints) < int(self.parameters["minimumEstimatesRequired"]):
            print "Getting point estimates"
            #We see a hole, we need to check every hole and append the values to the estimated AbstractCollocationFinder
	    for det in [detection for detection in self.detectionData if detection[0] == self.torpedoHoleClassNumber or detection[0] in self.fruitClassNumbers]:
                if det[1] >= 808 / 3.0 and det[1] < 2 * 808 /3.0:
  	            imgPoints = [(det[1] - (.5 * det[3]), det[2] - (.5* det[4])),(det[1] + (.5 * det[3]), det[2] - (.5* det[4])),
			 (det[1] + (.5 * det[3]), det[2] + (.5* det[4])),(det[1] - (.5 * det[3]), det[2] + (.5* det[4]))]
	            srcPoints = [(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0)]
	            rvec, tvec = cv2.solvePnP(np.array(srcPoints).astype('float32'), np.array(imgPoints).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
	            if tvec[2][0] <= float(self.parameters["getDistanceAway"]):
    		        self.reachedBoard = True
	            poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0] + float(self.parameters["xOffset"]), tvec[1][0], -tvec[2][0],0,0,0)
	            self.estimatedPoints.append([north/1.0, east/1.0, up, 0, 0,0])
	    if self.calculatedWaypoint == None:
	       self.calculatedWaypoint = self.position + self.orientation
            print "Don't see targets, getting closer"
            if len([det for det in self.detectionData if det[0] in self.classNumbers]) == 0:
               print "Lost detections, searching again..."
               self.finalWaypoint[2] = self.position[2]
               self.foundObstacles = False
               self.calculatedWaypoint = False
	       return -1
               #Move towards the torpedo board until we see a hole
            det = [detection for detection in self.detectionData if detection[0] in self.classNumbers][0]
            self.calculatedWaypoint = []
            if det[1] < 808 / 3.0:
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, -3, 0, 0)
                self.calculatedWaypoint = [n,e,u,y,0,0]
                print "Moving Left"
            elif det[1] >= 2 * 808 / 3.0:
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, +3, 0, 0)
                self.calculatedWaypoint = [n,e,u,y,0,0]
                print "moving Right"
            elif det[1] >= 808 / 3.0 and det[1] < 2 * 808 /3.0:
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,-5, 0, 0, 0)
                self.calculatedWaypoint = [n,e,u,y,0,0]
                print "moving forward"
	    self.moveToWaypoint(self.calculatedWaypoint)
	    return -1
        if self.reachedBoard == False and len(self.estimatedPoints) >= int(self.parameters["minimumEstimatesRequired"]):
                print "Got enought points, moving to board"

                northEstimate = (sorted(([v[0] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]
                eastEstimate = (sorted(([v[1] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]
                upEstimate = (sorted(([v[2] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]

                
                northEstimate -= float(self.parameters["getDistanceAway"]) * math.cos(math.radians(self.generalWaypoint[3]))
                eastEstimate -= float(self.parameters["getDistanceAway"]) * math.sin(math.radians(self.generalWaypoint[3]))
                self.calculatedWaypoint = [northEstimate, eastEstimate, upEstimate - int(self.parameters["depthOffset"]), self.generalWaypoint[3], 0,0]
                print "Goint to point:", self.calculatedWaypoint
                print "Estimated Depth was:", upEstimate
                if self.moveToWaypoint(self.calculatedWaypoint):
	            self.writeDebugMessage("Going to point: " + str(self.calculatedWaypoint))
		    if self.timesAttempted < int(self.parameters["numOfTries"]):
			self.foundObstacles = False
			self.estimatedPoints = []
			self.timesAttempted += 1
			self.writeDebugMessage("Finished attempt: " + str(self.timesAttempted))
			return -1
		    else:
			self.reachedBoard = True
                return -1

        if self.reachedBoard == True:
            print "Reached board, performing execution"
            return self.performExecution()

                

    def performExecution(self):
        if self.parameters["pullArm"] in ["True", "true", "t"] and not self.pulledArm:
            print "Pulling arm"
            self.pullArmFromCurrentLocation()
            return -1
            
	print "Made it past arm pull"
	if self.calculatedMoveDown == False:
	    poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, 0, 2, 0,0,0,0)
	    self.calculatedWaypoint = [north,east,up,yaw,0,0]
	    self.calculatedMoveDown = True
	if self.moveToWaypoint(self.calculatedWaypoint):
	    self.writeDebugMessage("In sight, would fire torpedo: " + str(self.calculatedWaypoint))


    def pullArmFromCurrentLocation(self): #This code will be used to 'hard code' the arm pulling
	print "Pulled Arm", self.pulledArm, "Above Arm", self.aboveArm, "Finished Pulling", self.finishedPulling
        if self.waitArmPullTimer == None:
            self.waitArmPullTimer = time.time()
        if time.time() - self.waitArmPullTimer >= self.armPullTime:
            self.waitArmPullTimer = None
            self.armWaypoint = None
            if self.aboveArm == False:
                self.aboveArm = True
            elif self.finishedPulling == False:
                self.finishedPulling = True
            else:
                self.pulledArm = True
        if self.armWaypoint == None:
            if self.aboveArm == False:
                poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, 3, -4, -float(self.parameters["getDistanceAway"]), 0, 0,0)
                self.armWaypoint = [north, east, up, yaw, 0, 0]
            elif self.finishedPulling == False:
                poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+self.position, 0, 4, 0, 0, 0,0)
                self.armWaypoint = [north, east, up, yaw, 0, 0]
            else:
                self.armWaypoint = self.calculatedWaypoint
                
        self.moveToWaypoint(self.armWaypoint)

        
    def torpedoIdentificationMethod1(self, value):
        thresh = float(self.parameters["torpedoThreshold"])
        for target in self.algorithm1Data:
            meanX = np.mean([t[0] for t in target])
            meanY = np.mean([t[1] for t in target])
            if math.sqrt((meanX - value[0]) ** 2 + (meanY - value[1]) ** 2) <= thresh:
                target = np.append(value, target)
                return self.algorithm1Data[0]
            
        self.algorithm1Data = np.append(np.array([value]), self.algorithm1Data)
        return self.algorithm1Data[0]


    def torpedoIdentificationMethod2(self, value): #value comes in as touple(xPixel,yPixel)
        self.SAMPLE_DATA.append(value);
	self.SAMPLE_DATA
		
