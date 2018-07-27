onLinux = True
if onLinux:
	import darknet as dn
	import PyCapture2 as pc2
import copy
from PyQt4 import QtCore, QtGui
import sys
import os
import cv2
import numpy as np
import time

useVideo = False
videoFile = "/media/sub_data/example3.mp4"


class yoloComputerVision(QtCore.QThread):

	def __init__(self):
		QtCore.QThread.__init__(self)
		self.getList = []

		self.dataFile = "/media/sub_data/data/7_22.data"
		self.weightFile = "/media/sub_data/weights/7_22_20000.weights"
		self.cfgFile = "/media/sub_data/cfg/7_22.cfg"

		self.frontCamera = None
		self.botCamera = None


		self.useVideo = False
		self.videoPath = "/media/sub_data/example3.mp4"

		self.srcPoints = [(0,0,0), (1,0,0), (2,0,0), (1, -.5, 0)]
		#Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....
		self.torpedoSrcPoints = [(0,0,0), (12,0,0), (5.5, -35.5, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0)] 
		self.cornerLocations = [(3, -5, 0), (3, 5, 0), (-3, 5, 0), (-3, 5, 0), (12, -3, 0), (12, 3, 0), (9, 3, 0), (9, -3,0), (9, -32, 0), (9, -39,0), (2, -39, 0), (2, -32,0)]
		self.torpedoSrcPoints = self.torpedoSrcPoints + self.cornerLocations

		self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2, "Cherry":3, "Banana":5, "Grape":4, "TLHTRC":5,"TLHBRC":6,"TLHBLC":7,"TLHTLC":8 } 
		self.srcPoints = []
		self.imgPoints = []


		self.activeCamera = None
		self.camMat = [[808, 0, 408],
			       [0, 608, 304],
			       [0,   0, 1]]
		if not onLinux:
			return

		dn.set_gpu(0)

		self.detectionDictionary = {}

		self.running = True

	def useBottomCamera(self):
		if self.botCamera != None:
			self.activeCamera = self.botCamera

	def useFrontCamera(self):
		if self.frontCamera != None:
			self.activeCamera = self.frontCamera

	def run(self):
		if not onLinux:
			return

		self.net = dn.load_net(self.cfgFile, self.weightFile, 0)
		self.meta = dn.load_meta(self.dataFile)
	
		dataFile = open(self.dataFile, "r")
		line = dataFile.readline()
		namesFile = None
		while line:
			line = line.replace(" ", "")
			line = line.split("=")
			if line[0] == "names":
				print "Names file:", line
				namesFile = open(line[1].replace("\n", ""), "r")
				break
			line = dataFile.readline()

		dataFile.close()
		if namesFile != None:
			line = namesFile.readline()
			index = 0
			while line:
				self.detectionDictionary[line.replace("\n", "")] = index
				index += 1
				line = namesFile.readline()	
		namesFile.close()

		if useVideo == True:
			video = cv2.VideoCapture(videoFile)
		else:
			bus = pc2.BusManager()
			self.activeCamera = pc2.Camera()
			self.frontCamera = pc2.Camera()
			self.botCamera = pc2.Camera()
			self.frontCamera.connect(bus.getCameraFromIndex(1))
			self.frontCamera.startCapture()
			time.sleep(1)
			self.botCamera.connect(bus.getCameraFromIndex(0))
			self.botCamera.startCapture()
			self.activeCamera = self.frontCamera

		while self.running == True:
                    if self.useVideo == False:
			self.image = self.activeCamera.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
                    else:
			t, img = self.activeCamera.read()
                    #yoloImage = dn.IMAGE()
                    detections = dn.detect_np(self.net, self.meta, img, thresh=.2, hier_thresh = .2)
                    newDetections = []
                    self.imgPoints = []
                    self.srcPoints = []
                    for detection in detections:
                            fixedClassNumber = self.detectionDictionary[detection[0]]
                            newDetections.append([fixedClassNumber, detection[1], detection[2]])
                            if detection[0] in self.torpedoDictionary or detection[0] == "Corner":
				if detection[0] != "Corner":
					pass
					self.imgPoints.append((detection[2][0], detection[2][1]))
					self.srcPoints.append(self.torpedoSrcPoints[self.torpedoDictionary[detection[0]]])
				elif detection[0] == "Corner":
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
									cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,0), -1)
									index = self.torpedoDictionary[secondDet[0]]
									index += 9
							elif detection[2][0] >= secondDet[2][0] + (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] + (.5 * secondDet[2][2]) + pixelError:
								if detection[2][1] <= secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError:
									cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (0,255,0), -1)
									index = self.torpedoDictionary[secondDet[0]]
									index += 6
							if detection[2][0] >= secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError:
								if detection[2][1] <= secondDet[2][1] + (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] + (.5 * secondDet[2][3]) - pixelError:
									cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (0,0,255), -1)
									index = self.torpedoDictionary[secondDet[0]]
									index += 8
							elif detection[2][0] >= secondDet[2][0] + (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] + (.5 * secondDet[2][2]) + pixelError:
								if detection[2][1] <= secondDet[2][1] + (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] + (.5 * secondDet[2][3]) - pixelError:
									cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,255), -1)
									index = self.torpedoDictionary[secondDet[0]]
									index += 7
							if index == None:
								pass
							else:
								self.srcPoints.append(self.torpedoSrcPoints[index])
								self.imgPoints.append((int(detection[2][0]), int(detection[2][1])))
					

                    if len(self.imgPoints) >= 4:
				#print self.imgPoints, self.srcPoints
				rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(self.imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]
				(pose1, jacobian) = cv2.projectPoints(np.array([(0.0,0.0,0.1)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
				(pose, jacobian) = cv2.projectPoints(np.array([(0,0,12.0)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
				cv2.line(img, (int(pose1[0][0][0]), int(pose1[0][0][1])), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 2)

		    for detection in detections:
			    loc = detection[2]
			    cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))
		    self.getList.append(newDetections)
		    cv2.imshow("Vision", img)
		self.activeCamera.stopCapture()

	def killThread(self):
		self.running = False

