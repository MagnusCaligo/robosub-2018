import darknet as dn
import copy
from PyQt4 import QtCore, QtGui
import sys
import os
import PyCapture2 as pc2
import cv2
import numpy as np
import time


class yoloComputerVision(QtCore.QThread):

	def __init__(self):
		QtCore.QThread.__init__(self)

		self.dataFile = "/media/sub_data/data/test.data"
		self.weightFile = "/media/sub_data/6_15_test_40000.weights"
		self.cfgFile = "/media/sub_data/cfg/6_15_test.cfg"

		self.srcPoints = [(0,0,0), (1,0,0), (2,0,0), (1, -.5, 0)]

		self.camMat = [[808, 0, 408],
			       [0, 608, 304],
			       [0,   0, 1]]

		dn.set_gpu(0)

		self.detectionDictionary = {}

		self.getList = []
		self.running = True

	def run(self):

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

		bus = pc2.BusManager()
		self.cam = pc2.Camera()
		self.cam.connect(bus.getCameraFromIndex(0))
		self.cam.startCapture()

		#video = cv2.VideoCapture("/media/sub_data/gateVideo.avi")


		while self.running == True:
			self.image = self.cam.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
			#t, img = video.read()
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
				
				rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]

				(pose, jacobian) = cv2.projectPoints(np.array([(0,0,1.0)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
				cv2.line(img, (int(banana[2][0]), int(banana[2][1])), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 2)



			self.getList.append(newDetections)
			cv2.imshow("Vision", img)
		self.cam.stopCapture()

	def killThread(self):
		self.running = False

class yoloSimplified:

	def __init__(self):

		self.dataFile = "/media/sub_data/data/test.data"
		self.weightFile = "/media/sub_data/6_15_test_40000.weights"
		self.cfgFile = "/media/sub_data/cfg/6_15_test.cfg"

		self.srcPoints = [(0,0,0), (1,0,0), (2,0,0), (1, -.5, 0)]

		self.camMat = [[808, 0, 408],
			       [0, 608, 304],
			       [0,   0, 1]]

		dn.set_gpu(0)

		self.detectionDictionary = {}

		self.getList = []
		self.running = True

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

		bus = pc2.BusManager()
		self.cam = pc2.Camera()
		self.cam.connect(bus.getCameraFromIndex(0))
		self.cam.startCapture()

		#video = cv2.VideoCapture("/media/sub_data/gateVideo.avi")


		while self.running == True:
			self.image = self.cam.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
			#t, img = video.read()
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
				#loc = detection[2]
				#cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

			#if seeFruits[8] + seeFruits[9] + seeFruits[10] + seeFruits[11] == 4:
			if seeFruits[11] == 1:
				'''cherry = seeFruits[12]
				banana = seeFruits[13]
				grape = seeFruits[14]'''
				board = seeFruits[15]
				'''bx = int(board[2][0] - (board[2][2]/2))
				by = int(board[2][1] - (board[2][3]/2))
				imgPoints = [(int(cherry[2][0]), int(cherry[2][1])),(int(banana[2][0]), int(banana[2][1])),(int(grape[2][0]), int(grape[2][1])), (bx,by)]'''
				
				x1 = int(board[2][0] - (board[2][2] * .5))
				y1 = int(board[2][1] - (board[2][3] * .5))
				x2 = int(board[2][0] + (board[2][2] * .5))
				y2 = int(board[2][1] + (board[2][3] * .5))

				h,w = img.shape[:2]
				buff = 50

				x1 = min(max(x1-buff, 0), w-1)
				y1 = min(max(y1-buff, 0), h-1)
				x2 = min(max(x2+buff, 0), w-1)
				y2 = min(max(y2+buff, 0), h-1)

				roi = img[y1:y2, x1:x2]
				_min = cv2.getTrackbarPos("min", "Vision")
				_max = cv2.getTrackbarPos("max", "Vision")
				roic = cv2.Canny(roi, _min, _max)
				cv2.imshow("ROI", roic)


				ret, thresh = cv2.threshold(roic, 128, 255, 0)
				contours, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
				#print "Contours", contours
				#cv2.drawContours(roi, contours, -1, (255,0,0), 3)
				total = []
				for c in contours:
					# approximate the contour
					peri = cv2.arcLength(c, True)
					approx = cv2.approxPolyDP(c, 0.02 * peri, True)
				 
					# if our approximated contour has four points, then
					# we can assume that we have found our screen
					if len(approx) == 4:
						total.append(approx)
				cv2.drawContours(roi, total, -1, (255, 0, 0), 3)
				'''lines = cv2.HoughLinesP(roi,1,np.pi/180,200, 100, 10)
				print "Lines:", lines
				if lines != None:
					for x1, y1, x2, y2 in lines[0]:
						cv2.line(img, (x1, y1), (x2, y2), (255,0,0), 2)

				'''
				
				'''rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]

				(pose, jacobian) = cv2.projectPoints(np.array([(0,0,1.0)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
				cv2.line(img, (int(banana[2][0]), int(banana[2][1])), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 2)'''



			for detection in detections:
				loc = detection[2]
				cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

			self.getList.append(newDetections)
			cv2.imshow("Vision", img)
			key = cv2.waitKey(1)
			if key == ord('q'):
				self.running = False
		self.cam.stopCapture()

	def killThread(self):
		self.running = False

if __name__ == "__main__":
	cv = yoloSimplified()
	cv.run()

