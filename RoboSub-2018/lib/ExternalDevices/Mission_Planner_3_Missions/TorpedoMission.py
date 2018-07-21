from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class TorpedoMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "Torpedo Target = TL\ngetDistanceAway = 2\nminimumEstimatesRequired=20\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
	
        #Top Left, Top Right, Full Board, Bottom Hole, Cherry, Grape, Banana, Corner
        #self.classNumbers = [7, 8, 6,9,3,4,5,13]
        self.classNumbers = [8,9,10,11,12]
        self.torpedoHoleClassNumber = 12
        self.minimumToSee = 3


    def initalizeOnMissionStart(self):
        AbstractMission.initalizeOnMissionStart(self)

        self.estimatedPoints = []
        self.estimatedTorpedoLocation = []

        self.calculatedWaypoint = None
        
    
        #Flags
        self.reachedFinalWaypoint = False
        self.foundObstacles = False
        self.reachedBoard = False

        self.srcPoints = []
        self.imgPoints = []
        
        #Timing stuff
        self.rotateTimer = None
        self.rotateWaitTime = None
        self.waitTimer = None
        self.waitTime = 5

    def checkIfSeeObstacles(self):
        numWeSee = 0
        for detection in self.detectionData:
            if detection[0] in self.classNumbers:
                numWeSee += 1
        if numWeSee >= self.minimumToSee:
            return True
        return False


    def update(self):
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
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.position[2] - self.finalWaypoint[2],0, 45, 0,0);
                self.calculatedWaypoint = [self.finalWaypoint[0],self.finalWaypoint[1],self.finalWaypoint[2],yaw,pitch,roll]
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
		    print rvec, tvec
                    poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0], -tvec[2][0],0,0,0)
                    self.estimatedPoints.append([north/1.0, east/1.0, up, 0, 0,0])
                self.moveToWaypoint(self.calculatedWaypoint)
                return -1
            else:
		print "Don't see targets, getting closer"
		if len([det for det in self.detectionData if det[0] in self.classNumbers]) == 0:
			print "Lost detections, searching again..."
			self.foundObstacles = False
			return -1
                pass #Move towards the torpedo board until we see a hole
                det = [detection for detection in self.detectionData if detection[0] in self.classNumbers][0]
                self.calculatedWaypoint = []
                if det[1] < 808 / 3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, -1, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
                elif det[1] >= 2 * 808 / 3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,0, 1, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
                elif det[1] >= 808 / 3.0 and det[1] < 2 * 808 /3.0:
                    p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0,1,1, 0, 0, 0)
                    self.calculatedWaypoint = [n,e,u,y,p,r]
                self.moveToWaypoint(self.calculatedWaypoint)
                return -1
        if self.reachedBoard == False and len(self.estimatedPoints) >= int(self.parameters["minimumEstimatesRequired"]):
		print "Got enought points, moving to board"

                northEstimate = (sorted(([v[0] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]
                eastEstimate = (sorted(([v[1] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]
                upEstimate = (sorted(([v[2] for v in self.estimatedPoints])))[len(self.estimatedPoints)/2]

		print northEstimate, eastEstimate
		print "Distance:", math.sqrt(northEstimate**2 + eastEstimate**2)
                
                northEstimate -= float(self.parameters["getDistanceAway"]) * math.cos(math.radians(self.generalWaypoint[3]))
                eastEstimate -= float(self.parameters["getDistanceAway"]) * math.sin(math.radians(self.generalWaypoint[3]))
                self.calculatedWaypoint = [northEstimate, eastEstimate, 5, self.generalWaypoint[3], 0,0]
                if self.moveToWaypoint(self.calculatedWaypoint):
                    self.reachedBoard = True
                return -1

        if self.reachedBoard == True:
	    print "Reached board, waiting"
            if self.waitTimer == None:
                self.waitTimer = time.time()
            if self.waitTimer - time.time() >= self.waitTime:
                print "Finished Mission"
                return 1
            self.moveToWaypoint(self.calculatedWaypoint)

                




                    
            
        
        
            

		
