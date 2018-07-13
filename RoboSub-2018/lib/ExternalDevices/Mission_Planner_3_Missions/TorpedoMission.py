from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class TorpedoMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "Torpedo Target = TL\ngetDistanceAway = 2\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
	
	#Top Left, Top Right, Full Board, Bottom Hole, Cherry, Grape, Banana, Corner
	self.classNumbers = [7, 8, 6,9,3,4,5,13]
	self.minimumToSee = 3

	self.reachedFinalWaypoint = False
	

        self.torpedoSrcPoints = [(0,0,0), (12,0,0), (5.5, -35.5, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0)] 
        self.cornerLocations = [(3, -5, 0), (3, 5, 0), (-3, 5, 0), (-3, 5, 0), (12, -3, 0), (12, 3, 0), (9, 3, 0), (9, -3,0), (9, -32, 0), (9, -39,0), (2, -39, 0), (2, -32,0)]
        self.torpedoSrcPoints = self.torpedoSrcPoints + self.cornerLocations
	self.srcPoints = []
	self.imgPoints = []

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
			if detection[0] != self.classNumbers[-1]
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

		
