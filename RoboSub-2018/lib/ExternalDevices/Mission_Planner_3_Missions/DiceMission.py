from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class DiceMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "dice# = 0\ngetDistanceAway = 2\nminimumEstimations=100\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

    def initalizeOnMissionStart(self):
        AbstractMission.initalizeOnMissionStart(self)
            
        self.reachedFinalWaypoint = False
        self.detectionData = None
        self.lastKnownDepth = self.finalWaypoint[2]

        self.foundObstacles = False
        self.diceClassNumber = int(self.parameters["dice#"])
        self.positionEstimates = []

        self.sentMessage1 = False
        self.sentMessage2 = False
        self.sentMessage3 = False
        self.sentMessage4 = False
        self.sentMessage5 = False
        
        self.hitBuoy = False
        self.movingForward = True
        self.inFrontOfBuoy = False

        self.atBuoyTimer = None
        self.lookingForObstaclesTimer = None
        self.hitBuoyTimer = None
        
        self.rotateTimer = None
        self.rotateWaitTime = 8

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
                return True
        return False

    def sortThroughDetections(self):
        detections = []
        if self.detectionData != None:
            print "Detection Data is", self.detectionData
            for det in self.detectionData:
                if det[0] == int(self.parameters["dice#"]):
                    detections.append(det)
            return detections
        else:
            return None

    def update(self):
        if not self.reachedFinalWaypoint and not self.checkIfFoundObstacles():
            self.reachedFinalWaypoint = self.moveToWaypoint(self.finalWaypoint)
            print "Moving to waypoint"
            return -1
        else:
            self.reachedFinalWaypoint = True
            self.calculatedWaypoint = self.finalWaypoint

        if self.reachedFinalWaypoint and not self.checkIfFoundObstacles():
            print "At waypoint, looking for obstacle"
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.finalWaypoint[2] -self.position[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,self.finalWaypoint[2],yaw,0,0]
            self.moveToWaypoint(self.calculatedWaypoint);
            if self.checkIfFoundObstacles() == True:
                self.foundObstacles = True
            return -1
        
        for det in [detection for detection in self.detectionData if detection[0] == int(self.parameters["dice#"])]:
            imgPoints = [(det[1] - (.5 * det[3]), det[2] - (.5* det[4])),(det[1] + (.5 * det[3]), det[2] - (.5* det[4])),
                         (det[1] + (.5 * det[3]), det[2] + (.5* det[4])),(det[1] - (.5 * det[3]), det[2] + (.5* det[4]))]
            self.src_pts
            rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(imgPoints).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
            poseData, north, east, up, pitch, yaw, roll =	self.movementController.relativeMoveXYZ(self.orientation+self.position, tvec[0][0], tvec[1][0], -tvec[2][0],0,0,0)
            self.positionEstimates.append([north/1.0, east/1.0, up, 0, 0,0])

        #Hold position while getting data points
        if len(self.positionEstimates) <= int(self.parameters["minimumEstimates"]):
            self.moveToWaypoint(self.calculatedWaypoint)
        #Else if we have enough points start moving to the obstacle
        elif len(self.positionEstimates) >= int(self.parameters["minimumEstimates"]) and not self.inFrontOfBuoy:
            northEstimate = np.median(np.array([p[0] for p in self.positionEstimates]))
            eastEstimate = np.median(np.array([p[1] for p in self.positionEstimates]))
            upEstimate = np.median(np.array([p[2] for p in self.positionEstimates]))
            
            position = [northEstimate, eastEstimate, upEstimate]
            rotationDifference = math.degrees(math.atan2(position[1] - self.position[1], position[0] - self.position[0]))
            poseData, north, east, up, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation+position, 0, 0, int(self.parameters["getDistanceAway"]),0,0,0)
            self.calculatedWaypoint = [n, e, u, rotationDifference, 0, 0]
            self.inFrontOfBuoy = self.moveToWaypoint(self.calculatedWaypoint)
            
        elif self.inFrontOfBuoy:
            print "Trying to hit buoy"
            if self.hitBuoyTimer == None:
                self.hitBuoyTimer = time.time()
                self.writeDebugMessage("Moving Forward...")
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0, 0, -int(self.parameters["getDistanceAway"])-1, 0, 0, 0)
                self.diceWaypoint = [n,e,u,y,p,r]
            if time.time() - self.hitBuoyTimer >= self.hitBuoyMaxTime:
                if self.movingForward == False:
                    return 1 #Finished the mission
                self.movingForward = False
                self.writeDebugMessage("Moving Backward...")
                p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0.5, self.position[2] - self.depthAtRelativeMove, 3*int(self.parameters["getDistanceAway"]), 0, 0, 0)
                self.diceWaypoint = [n,e,u,y,p,r]
                self.hitBuoyTimer = time.time()
            if self.depthAtRelativeMove == None:
                self.depthAtRelativeMove = self.position[2]
            #self.movementController.advancedMove(poseData, north, east, up, 0, yaw, 0)
            self.moveToWaypoint(self.diceWaypoint)


            
        
        
        



