onLinux = False
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

            self.dataFile = "/media/sub_data/data/test.data"
            self.weightFile = "/media/sub_data/6_15_test_40000.weights"
            self.cfgFile = "/media/sub_data/cfg/6_15_test.cfg"

            self.useVideo = True
            self.videoPath = "/media/sub_data/gateVideo.avi"

            self.activeCamera = None

            #Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....
            self.torpedoSrcPoints = [(0,0,0), (1,0,0), (.5, -3, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0)] 
            self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2, "Cherry":3, "Banana":4, "Grape":5} 
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
            self.activeCamera.connect(bus.getCameraFromIndex(1))
            self.activeCamera.startCapture()

        def useFrontCamera(self):
            if self.activeCamera != None:
                self.activeCamera.stopCapture()
            self.activeCamera.connect(bus.getCameraFromIndex(0))
            self.activeCamera.startCapture()

	def run(self):

		self.net = dn.load_net(self.cfgFile, self.weightFile, 0)
		self.meta = dn.load_meta(self.dataFile)
		def nothing(t):
			pass

		cv2.namedWindow("Vision")
		cv2.createTrackbar("min", "Vision", 0, 255, nothing)
		cv2.createTrackbar("max", "Vision", 0, 255, nothing)
	
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
                    self.activeCamera = cv2.VideoCapture(self.videFile)



		while self.running == True:
                    if self.useVideo == False:
			self.image = self.activeCamera.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
                    else:
			t, img = self.activeCam.read()
                    #yoloImage = dn.IMAGE()
                    detections = dn.detect_np(self.net, self.meta, img, thesh=.2, hier_thresh = .2)
                    newDetections = []
                    self.imgPoints = []
                    self.srcPoints = []
                    for detection in detections:
                            fixedClassNumber = self.detectionDictionary[detection[0]]
                            newDetections.append([fixedClassNumber, detection[1], detection[2]])
                            if fixedClassNumber in seeFruits:
                                    seeFruits[fixedClassNumber] = 1
                                    seeFruits[fixedClassNumber +4] = [fixedClassNumber, detection[1], detection[2]]
                            #loc = detection[2]
                            #cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

                            if detection[0] in self.torpedoDictionary:
                                self.imgPoints.append((detection[1][0], detection[1][1]))
                                self.srcPoints.append(self.torpedoDictionary[detection[0]])

                    if len(self.imgPoints) >= 4:
                        rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(self.imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]

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

