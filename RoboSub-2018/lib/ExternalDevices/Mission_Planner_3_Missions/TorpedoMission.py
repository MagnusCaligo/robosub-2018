from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class TorpedoMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "Torpedo Target = TL\ngetDistanceAway = 2\nminimumEstimatesRequired=200\npullArm=True\ntorpedoThreshold = 60"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
	
        #Top Left, Top Right, Full Board, Bottom Hole, Cherry, Grape, Banana, Corner
        #self.classNumbers = [7, 8, 6,9,3,4,5,13]
        self.classNumbers = [8,9,10,11,12]
        self.torpedoHoleClassNumber = 12
        self.minimumToSee = 2


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
        if not self.pulledArm:
            self.pullArmFromCurrentLocation()
            return -1
        else:
            return 1
        #Move to waypoint or move on if you see the board
        if not self.reachedFinalWaypoint and not self.checkIfSeeObstacles:
            self.reachedFinalWaypoint = self.moveToWaypoint(self.finalWaypoint)
	    print "Moving to waypoint"
            return -1
        else:
            self.reachedFinalWaypoint = True

        if self.reachedFinalWaypoint and not self.foundObstacles:
            print "At waypoint, looking for obstacle"
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.finalWaypoint[2] -self.position[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,u,yaw,0,0]
		print "Depth is", u
            self.moveToWaypoint(self.calculatedWaypoint);
            if self.checkIfSeeObstacles() == True:
                self.foundObstacles = True
            return -1
            
        if len(self.estimatedPoints) < int(self.parameters["minimumEstimatesRequired"]):
            print "Getting point estimates"
            if self.torpedoHoleClassNumber in [det[0] for det in self.detectionData]:
                #We see a hole, we need to check every hole and append the values to the estimated AbstractCollocationFinder
                for det in [detection for detection in self.detectionData if detection[0] == self.torpedoHoleClassNumber]:
                    imgPoints = [(det[1] - (.5 * det[3]), det[2] - (.5* det[4])),(det[1] + (.5 * det[3]), det[2] - (.5* det[4])),
                                 (det[1] + (.5 * det[3]), det[2] + (.5* det[4])),(det[1] - (.5 * det[3]), det[2] + (.5* det[4]))]
                    srcPoints = [(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0)]
                    rvec, tvec = cv2.solvePnP(np.array(srcPoints).astype('float32'), np.array(imgPoints).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
                    poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0], -tvec[2][0],0,0,0)
                    self.estimatedPoints.append([north/1.0, east/1.0, up, 0, 0,0])
                self.moveToWaypoint(self.calculatedWaypoint)
                return -1
            else:
                print "Don't see targets, getting closer"
                if len([det for det in self.detectionData if det[0] in self.classNumbers]) == 0:
                    print "Lost detections, searching again..."
		    self.finalWaypoint[2] = self.position[2]
                    self.foundObstacles = False
		    self.calculatedWaypoint = False
		    self.estimatedPoints = []
                    return -1
                #Move towards the torpedo board until we see a hole
                det = [detection for detection in self.detectionData if detection[0] in self.classNumbers][0]
                self.calculatedWaypoint = []
                if det[1] < 808 / 3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, -1, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
		    print "Moving Left"
                elif det[1] >= 2 * 808 / 3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, 1, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
		    print "moving Right"
                elif det[1] >= 808 / 3.0 and det[1] < 2 * 808 /3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,1, 0, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
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
                self.calculatedWaypoint = [northEstimate, eastEstimate, upEstimate, self.generalWaypoint[3], 0,0]
                print "Goint to point:", self.calculatedWaypoint
                print "Estimated Depth was:", upEstimate
                if self.moveToWaypoint(self.calculatedWaypoint):
                    self.reachedBoard = True
                    self.estimatedPoints = []
                return -1

        if self.reachedBoard == True:
	    print "Reached board, performing execution"
            return self.performExecution()

                

    def performExecution(self):
        if self.parameters["pullArm"] in ["True", "true", "t"] and not self.pulledArm:
	    print "Pulling arm"
            self.pullArmFromCurrentLocation()
            return -1
            
        target = []
        if len(self.estimatedPoints) < int(self.parameters["minimumEstimatesRequired"]):
            if self.torpedoHoleClassNumber in [det[0] for det in self.detectionData]:
                #We see a hole, we need to check every hole and append the values to the estimated AbstractCollocationFinder
                for det in [detection for detection in self.detectionData if detection[0] == self.torpedoHoleClassNumber]:
                    target = self.torpedoIdentificationMethod1((det[1][0], det[1][1]))
                    #target = self.torpedoIdentificationMethod2((det[1][0], det[1][1]))
                self.moveToWaypoint(self.calculatedWaypoint)
                return -1


    def pullArmFromCurrentLocation(self): #This code will be used to 'hard code' the arm pulling
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
                poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, 1, -2, -float(self.parameters["getDistanceAway"]), 0, 0,0)
                self.armWaypoint = [north, east, up, yaw, pitch, roll]
            elif self.finishedPulling == False:
                poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, 0, 2, 0, 0, 0,0)
                self.armWaypoint = [north, east, up, yaw, pitch, roll]
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

                



                    
            
        
        
            

		
