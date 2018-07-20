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

        self.estimatedPoints = []
        self.estimatedTorpedoLocation = []

        self.reachedFinalWaypoint = False
        self.calculatedWaypoint = None
        
    
        #Flags
        self.foundObstacles = False

        self.torpedoSrcPoints = [(0,0,0), (12,0,0), (5.5, -35.5, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0)] 
        self.cornerLocations = [(3, -5, 0), (3, 5, 0), (-3, 5, 0), (-3, 5, 0), (12, -3, 0), (12, 3, 0), (9, 3, 0), (9, -3,0), (9, -32, 0), (9, -39,0), (2, -39, 0), (2, -32,0)]
        self.torpedoSrcPoints = self.torpedoSrcPoints + self.cornerLocations
        self.srcPoints = []
        self.imgPoints = []
        
        #Timing stuff
        self.rotateTimer = None
        self.rotateWaitTime = None

    def initalizeOnMissionStart(self):
        AbstractMission.initalizeOnMissionStart(self)

    def checkIfSeeObstacles(self):
        numWeSee = 0
        for detection in self.detectionData:
            if detection[0] in self.classNumbers:
                numWeSee += 1
        if numWeSee >= self.minimumToSee:
            return True
        return False

    def isolateDetections(self):
	    for detection in self.detectionData:
		    if detection[0] in self.classNumbers:
			if detection[0] != self.classNumbers[-1]:
				self.imgPoints.append((detection[2][0], detection[2][1]))
				self.srcPoints.append(self.torpedoSrcPoints[self.torpedoDictionary[detection[0]]])
			elif detection[0] == self.classNumbers[-1]:
				print "Found a corner"
				pixelError = 20
				'''cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,0), -1)
				while True:
					cv2.imshow("Vision", img)
					if cv2.waitKey(1) == ord(" "):
						break'''
				for secondDet in detections:
					'''cv2.rectangle(img, (int(secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError ),int(secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError)), (int(secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError),int(secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError)), (255, 0, 0), 3)
					cv2.rectangle(img, (int(secondDet[2][0]-(.5 * secondDet[2][2])), int(secondDet[2][1]- (.5 * secondDet[2][3]))), (int(secondDet[2][0] + (.5*secondDet[2][2])), int(secondDet[2][1] + (.5*secondDet[2][3]))), (0,0,255))
					while True:
						cv2.imshow("Vision", img)
						if cv2.waitKey(1) == ord(" "):
							break'''
					if secondDet[0] in self.torpedoDictionary:
						index = None
						if detection[2][0] >= secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError:
							if detection[2][1] <= secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError:
								print "In top left corner of", secondDet[0]
								cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,0), -1)
								index = self.torpedoDictionary[secondDet[0]]
								index += 6
						elif detection[2][0] >= secondDet[2][0] + (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] + (.5 * secondDet[2][2]) + pixelError:
							if detection[2][1] <= secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError:
								print "In top right corner of", secondDet[0]
								cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (0,255,0), -1)
								index = self.torpedoDictionary[secondDet[0]]
								index += 3
						if detection[2][0] >= secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError:
							if detection[2][1] <= secondDet[2][1] + (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] + (.5 * secondDet[2][3]) - pixelError:
								print "In bottom left corner of", secondDet[0]
								cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (0,0,255), -1)
								index = self.torpedoDictionary[secondDet[0]]
								index += 5
						elif detection[2][0] >= secondDet[2][0] + (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] + (.5 * secondDet[2][2]) + pixelError:
							if detection[2][1] <= secondDet[2][1] + (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] + (.5 * secondDet[2][3]) - pixelError:
								print "In bottom right corner of", secondDet[0]
								cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,255), -1)
								index = self.torpedoDictionary[secondDet[0]]
								index += 4
						if index == None:
							pass
						else:
							index += 3
							self.srcPoints.append(self.torpedoSrcPoints[index])
							self.imgPoints.append((int(detection[2][0]), int(detection[2][1])))

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
            return -1
        elif self.checkIfSeeObstacles():
            self.foundObstacles = True
            
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
                    
            
        
        
            

		
