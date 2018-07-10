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
		if not onLinux:
			return

		self.dataFile = "/media/sub_data/data/justGates.data"
		self.weightFile = "/media/sub_data/weights/justGatesYoloTinyv3.backup"
		self.cfgFile = "/media/sub_data/cfg/tinyYoloV3-justGates.cfg"

		self.srcPoints = [(0,0,0), (1,0,0), (2,0,0), (1, -.5, 0)]

		self.activeCamera = None
		self.activeCameraMat = [[808, 0, 408],
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
			self.activeCamera.connect(bus.getCameraFromIndex(0))
			self.activeCamera.startCapture()



		while self.running == True:
			if useVideo == True:
				t, img = video.read()
				if t == False:
					video = cv2.VideoCapture(videoFile)
					continue
			else:
				self.image = self.activeCamera.retrieveBuffer()
				self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
				img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
				img = cv2.flip(img, -1)
			yoloImage = dn.IMAGE()
			detections = dn.detect_np(self.net, self.meta, img)
			newDetections = []
			seeFruits = {8:0, 9:0, 10:0, 11:0}
			for detection in detections:
				fixedClassNumber = self.detectionDictionary[detection[0]]
				newDetections.append([fixedClassNumber, detection[1], detection[2]])
				if fixedClassNumber in seeFruits:
					seeFruits[fixedClassNumber] = 1
					seeFruits[fixedClassNumber +4] = [fixedClassNumber, detection[1], detection[2]]
				loc = detection[2]
				cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

			if seeFruits[8] + seeFruits[9] + seeFruits[10] +seeFruits[11] == 4:
				cherry = seeFruits[12]
				banana = seeFruits[13]
				grape = seeFruits[14]	
				board = seeFruits[15]
				bx = int(board[2][0] + (board[2][2]/2))
				by = int(board[2][1] + (board[2][3]/2))

				imgPoints = [(int(cherry[2][0]), int(cherry[2][1])),(int(banana[2][0]), int(banana[2][1])),(int(grape[2][0]), int(grape[2][1])), (bx,by)]
				
				rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(imgPoints).astype("float32"), np.array(self.activeCameraMat).astype("float32"), np.zeros((4,1)))[-2:]

				(pose, jacobian) = cv2.projectPoints(np.array([(0,0,1.0)]), rvec, tvec, np.array(self.activeCameraMat).astype("float32"), None)
				cv2.line(img, (int(banana[2][0]), int(banana[2][1])), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 2)



			self.getList.append(newDetections)
			cv2.imshow("Vision", img)
		self.activeCamera.stopCapture()

	def killThread(self):
		self.running = False

