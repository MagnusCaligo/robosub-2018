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

            self.useVideo = False 
            self.videoPath = "/media/sub_data/example3.mp4"

	    self.usePicture = True
	    self.picturePath = "../../0.png"

            self.activeCamera = None

            #Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....
            self.torpedoSrcPoints = [(0,0,0), (12,0,0), (5.5, -35.5, 0), (-.25, -.5, 0), (.5, -.5, 0), (1, -.5, 0)] 
	    self.cornerLocations = [(3, -5, 0), (3, 5, 0), (-3, 5, 0), (-3, 5, 0), (12, -3, 0), (12, 3, 0), (9, 3, 0), (9, -3,0), (9, -32, 0), (9, -39,0), (2, -39, 0), (2, -32,0)]
	    self.torpedoSrcPoints = self.torpedoSrcPoints + self.cornerLocations

            self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2}#, "Cherry":3, "Banana":4, "Grape":5, "TLHTRC":5,"TLHBRC":6,"TLHBLC":7,"TLHTLC":8 } 
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

                if self.useVideo == False and self.usePicture == False:
                    bus = pc2.BusManager()
                    self.activeCamera = pc2.Camera()
                    self.activeCamera.connect(bus.getCameraFromIndex(0))
                    self.activeCamera.startCapture()
                elif self.useVideo == True:
                    self.activeCamera = cv2.VideoCapture(self.videoPath)
		elif self.usePicture == True:
		    self.sourceImg = cv2.imread(self.picturePath)
	



		while self.running == True:
                    if self.useVideo == False and self.usePicture == False:
			self.image = self.activeCamera.retrieveBuffer()
			self.image = self.image.convert(pc2.PIXEL_FORMAT.BGR)
			img = np.array(self.image.getData(), dtype="uint8").reshape((self.image.getRows(), self.image.getCols(), 3))
			img = cv2.flip(img, -1)
                    elif self.useVideo == True:
			t, img = self.activeCamera.read()
		    else:
			img = copy.copy(self.sourceImg)
                    #yoloImage = dn.IMAGE()
		    w, h, c = img.shape
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
					print "Detection", detection[0]
					if detection[0] == "Top Right Hole":
						pixelError = 20
						x, y, width, height = detection[2]
						x1, y1, x2, y2 = x + (.5*width)+pixelError, y + (.5*height)+pixelError,x + (.5*width)+pixelError, y + (.5*height)+pixelError, 
						
						if x1 < 0:
							x1 = 0
						if y1 < 0:
							y1 = 0
						if x2 >= w:
							x2 = w -1
						if y2 >= h:
							y2 = h -1
						print "Sub img", x1, y1, x2, y2
						subImg = img[int(y1):int(y2), int(x1):int(x2)]
						while True:
							cv2.imshow("Sub", subImg)
							if cv2.waitKey(1) == ord("q"):
								break
 
							
						
					
				elif detection[0] == "Corner" and False:
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
					

                    if len(self.imgPoints) >= 4:
			print "Solving..."
			#print self.imgPoints, self.srcPoints
                        rvec, tvec = cv2.solvePnP(np.array(self.srcPoints).astype("float32"), np.array(self.imgPoints).astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)))[-2:]
			(pose1, jacobian) = cv2.projectPoints(np.array([(0.0,0.0,0.1)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
			(pose, jacobian) = cv2.projectPoints(np.array([(0,0,12.0)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
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

