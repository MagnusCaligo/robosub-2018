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
            return -1
        else:
            self.reachedFinalWaypoint = True

        if self.reachedFinalWaypoint and not self.foundObstacles:
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.position[2] - self.finalWaypoint[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,u,yaw,pitch,roll]
            self.moveToWaypoint(self.calculatedWaypoint);
            if self.checkIfSeeObstacles() == True:
                self.foundObstacles = True
            return -1
            
        if len(self.estimatedPoints) < int(self.parameters["minimumEstimatesRequired"]):
            if self.torpedoHoleClassNumber in [det[0] for det in self.detectionData]:
                #We see a hole, we need to check every hole and append the values to the estimated AbstractCollocationFinder
                for det in [detection for detection in self.detectionData if detection[0] == self.torpedoHoleClassNumber]:
                    imgPoints = [(det[1] - (.5 * det[3]), det[2] - (.5* det[4])),(det[1] + (.5 * det[3]), det[2] - (.5* det[4])),
                                 (det[1] + (.5 * det[3]), det[2] + (.5* det[4])),(det[1] - (.5 * det[3]), det[2] + (.5* det[4]))]
                    srcPoints = [(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0)]
                    rvec, tvec = cv2.solvePnP(np.array(srcPoints).astype('float32'), np.array(imgPoints).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
                    poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0] + 1, tvec[2][0] - float(self.parameters["distanceThrough"]),0,0,0)
                    self.estimatedPoints.append([north, east, up, 0, 0,0])
                self.moveToWaypoint(self.calculatedWaypoint)
                return -1
            else:
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
                northEstimate = (([v[0] for v in self.estimatedPoints]).sort())[len(self.estimatedPoints)/2]
                eastEstimate = (([v[1] for v in self.estimatedPoints]).sort())[len(self.estimatedPoints)/2]
                upEstimate = (([v[2] for v in self.estimatedPoints]).sort())[len(self.estimatedPoints)/2]
                
                northEstimate -= float(self.parameters["getDistanceAway"]) * math.cos(math.radians(self.generalWaypoint[3]))
                eastEstimate -= float(self.parameters["getDistanceAway"]) * math.sin(math.radians(self.generalWaypoint[3]))
                self.calculatedWaypoint = [northEstimate, eastEstimate, upEstimate, self.generalWaypoint[3], 0,0]
                if self.moveToWaypoint(self.calculatedWaypoint):
                    self.reachedBoard = True
                return -1

        if self.reachedBoard == True:
            if self.waitTimer == None:
                self.waitTimer = time.time()
            if self.waitTimer - time.time() >= self.waitTime:
                print "Finished Mission"
                return 1
            self.moveToWaypoint(self.calculatedWaypoint)

                




                    
            
        
        
            

		
