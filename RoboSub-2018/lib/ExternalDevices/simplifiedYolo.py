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

class yoloSimplified:

	def __init__(self):

            self.dataFile = "/media/sub_data/data/7_2.data"
            self.weightFile = "/media/sub_data/weights/7_9_v2.weights"
            self.cfgFile = "/media/sub_data/cfg/7_9_v2.cfg"

            self.useVideo = True
            self.videoPath = "/media/sub_data/example3.mp4"

            self.activeCamera = None

            #Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....
            self.torpedoSrcPoints = [(0,0,0), (1,0,0), (.5, -3, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0), (.25, .25, 0), (.25, -.25, 0), (-.25, -.25, 0), (-.25, .25, 0)] 
            self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2, "Cherry":3, "Banana":4, "Grape":5, "TLHTRC":5,"TLHBRC":6,"TLHBLC":7,"TLHTLC":8 } 
            self.srcPoints = []
            self.imgPoints = []


            self.torpedoBoardOrientation = []

            self.camMat = [[808, 0, 408],
                           [0, 608, 304],
                           [0,   0, 1]]

            dn.set_gpu(0)

            self.detectionDictionary = {}

            self.getList = []
            self.running = True

        def useBottomCamera(self):
            if self.activeCamera != None:
                self.activeCamera.stopCapture()
	    bus = pc2.BusManager()
            self.activeCamera.connect(bus.getCameraFromIndex(1))
            self.activeCamera.startCapture()

        def useFrontCamera(self):
            if self.activeCamera != None:
                self.activeCamera.stopCapture()
	    bus = pc2.BusManager()
            self.activeCamera.connect(bus.getCameraFromIndex(0))
            self.activeCamera.startCapture()

	def run(self):

		self.net = dn.load_net(self.cfgFile, self.weightFile, 0)
		self.meta = dn.load_meta(self.dataFile)
		def nothing(t):
			pass

		cv2.namedWindow("Vision")
	
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

                if self.useVideo == False:
                    bus = pc2.BusManager()
                    self.activeCamera = pc2.Camera()
                    self.activeCamera.connect(bus.getCameraFromIndex(0))
                    self.activeCamera.startCapture()
                else:
                    self.activeCamera = cv2.VideoCapture(self.videoPath)



		while self.running == True:
                    if self.useVideo == False:
			self.image = self.activeCamera.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
                    else:
			t, img = self.activeCamera.read()
                    #yoloImage = dn.IMAGE()
                    detections = dn.detect_np(self.net, self.meta, img, thresh=.1, hier_thresh = .1)
                    newDetections = []
                    self.imgPoints = []
                    self.srcPoints = []
                    for detection in detections:
                            fixedClassNumber = self.detectionDictionary[detection[0]]
                            newDetections.append([fixedClassNumber, detection[1], detection[2]])
                            if detection[0] in self.torpedoDictionary or detection[0] == "Corner":
				if detection[0] != "Corner":
					self.imgPoints.append((detection[2][0], detection[2][1]))
					self.srcPoints.append(self.torpedoSrcPoints[self.torpedoDictionary[detection[0]]])
				elif detection[0] == "Corner":
					print "Found a corner"
					pixelError = 20
					cv2.circle(img, (int(detection[2][0]), int(detection[2][1])), 10, (255,0,0), -1)
					while True:
						cv2.imshow("Vision", img)
						if cv2.waitKey(1) == ord(" "):
							break
					for secondDet in detections:
						'''cv2.rectangle(img, (int(secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError ),int(secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError)), (int(secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError),int(secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError)), (255, 0, 0), 3)
						cv2.rectangle(img, (int(secondDet[2][0]-(.5 * secondDet[2][2])), int(secondDet[2][1]- (.5 * secondDet[2][3]))), (int(secondDet[2][0] + (.5*secondDet[2][2])), int(secondDet[2][1] + (.5*secondDet[2][3]))), (0,0,255))
						while True:
							cv2.imshow("Vision", img)
							if cv2.waitKey(1) == ord(" "):
								break'''
						if secondDet[0] in self.torpedoDictionary:
							if detection[2][0] >= secondDet[2][0] - (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] - (.5 * secondDet[2][2]) + pixelError:
								if detection[2][1] <= secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError:
									print "In top left corner of", secondDet[0]
									index = self.torpedoDictionary[secondDet[0]]
									index += 8
							elif detection[2][0] >= secondDet[2][0] + (.5 * secondDet[2][2]) - pixelError and detection[2][0] <= secondDet[2][0] + (.5 * secondDet[2][2]) + pixelError:
								if detection[2][1] <= secondDet[2][1] - (.5 * secondDet[2][3]) + pixelError and detection[2][1] > secondDet[2][1] - (.5 * secondDet[2][3]) - pixelError:
									print "In top right corner of", secondDet[0]
									index = self.torpedoDictionary[secondDet[0]]
									index += 9

                    if len(self.imgPoints) >= 4:
			print "Solving..."
			#print self.imgPoints, self.srcPoints
                        rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(self.imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]
			(pose1, jacobian) = cv2.projectPoints(np.array([(0.0,0.0,0.1)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
			(pose, jacobian) = cv2.projectPoints(np.array([(0,0,1.0)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
			cv2.line(img, (int(pose1[0][0][0]), int(pose1[0][0][1])), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 2)
			print "Rvec:", rvec ,"\n"
			print "Tvec:", tvec
			s =  time.time()
			while time.time() - s < 0:
				cv2.imshow("Vision", img)
				k = cv2.waitKey(1)
				if k == ord(" "):
					break

                    for detection in detections:
                            loc = detection[2]
                            cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

                    self.getList.append(newDetections)
                    cv2.imshow("Vision", img)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                            self.running = False
		self.activeCamera.stopCapture()

	def killThread(self):
		self.running = False

if __name__ == "__main__":
	cv = yoloSimplified()
	cv.run()

