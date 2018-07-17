onLinux = True
import math
if onLinux:
	import darknet as dn
import copy
from PyQt4 import QtCore, QtGui
import sys
import os
import cv2
import numpy as np
import time

class yoloSimplified:

	def __init__(self):

            self.dataFile = "/home/mechatronics/darknet/7_13_2/test.data"
            self.weightFile = "/home/mechatronics/darknet/7_13_2/weights/yolov3-tiny.backup"
            self.cfgFile = "/home/mechatronics/darknet/7_13_2/yolov3-tiny.cfg"

            self.useVideo = True 
            self.videoPath = "Downloads/example3.mp4"

	    self.usePicture = True
	    self.picturePath = "darknet/allLabeledImages/99.jpg"

            self.activeCamera = None

            #Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....

            self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2}#, "Cherry":3, "Banana":4, "Grape":5, "TLHTRC":5,"TLHBRC":6,"TLHBLC":7,"TLHTLC":8 } 

            self.camMat = [[808, 0, 404],
                           [0, 608, 304],
                           [0,   0, 1]]

            dn.set_gpu(0)
            self.fourcc = cv2.VideoWriter_fourcc(*"H264")
            self.outputVideo = cv2.VideoWriter("output.avi", self.fourcc, 30, (808, 608))


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
                        if t == False:
                            break
		    else:
			img = copy.copy(self.sourceImg)
                    #yoloImage = dn.IMAGE()
		    h,w, c = img.shape
                    print "SIZE:", h, w
                    detections = dn.detect_np(self.net, self.meta, img, thresh=.1, hier_thresh = .1)
                    newDetections = []
                    for detection in detections:
                            fixedClassNumber = self.detectionDictionary[detection[0]]
                            newDetections.append([fixedClassNumber, detection[1], detection[2]])
                            if detection[0] == "Torpedo Hole":
                                error = 20
                                x1 = int(detection[2][0] - (.5 * detection[2][2])) - error
                                x2 = int(detection[2][0] + (.5 * detection[2][2])) + error
                                y1 = int(detection[2][1] - (.5 * detection[2][3])) - error
                                y2 = int(detection[2][1] + (.5 * detection[2][3])) + error
                                if x1 < 0:
                                    x1 = 0
                                if y1 < 0:
                                    y1 = 0
                                if x2 >= w:
                                    x2 = w -1
                                if y2 >= h:
                                    y2 = h -1
                                subImg = copy.copy(img[y1:y2, x1:x2])
                                if np.prod(subImg.shape) == 0:
                                    continue
                                res = cv2.cvtColor(subImg, cv2.COLOR_RGB2HSV)
                                #kernel = np.ones((5,4), np.float32)/25
                                #binImg = cv2.filter2D(res, -1, kernel)

                                print "Sub shape", subImg.shape
                                print "Res shape", res.shape
                                mask = cv2.inRange(res, np.array([120, 0,0]), np.array([130,255,255]))
                                binImg = cv2.bitwise_and(subImg, subImg, mask=mask)
                                cv2.imshow("Binary", binImg)

                                cannyImg = cv2.Canny(binImg, 300, 700, 3)
                                #subImg = copy.copy(cannyImg)
                                cv2.imshow("Canny", cannyImg)
                                h,w = subImg.shape[:2]
                                center = (w/2, h/2)
                                pose = [[[center[0], center[1]]]]

                                _, contours, hierarchy = cv2.findContours(cannyImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                if len(contours) > 0:
                                    app = contours[0]
                                    largestArea = 0
                                    for cont in contours:
                                        a = cv2.contourArea(cont)
                                        if a > largestArea:
                                            app = cont


                                    val = .01
                                    epsilon = val * cv2.arcLength(app, True)
                                    app = cv2.approxPolyDP(app, epsilon, True)
                                    app = [app]
                                    cv2.drawContours(subImg, app, -1, (0,255,0), 1)

                                    topLeft = []
                                    topRight = []
                                    botRight = []
                                    botLeft = []

                                    def distance(p0, p1):
                                        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1]) ** 2)

                                    for pointSrc in app[0]:
                                        point = pointSrc[0]
                                        if point[0] in range(center[0], w):
                                            if point[1] in range(center[1], h):
                                                if len(botRight) == 0:
                                                    botRight = point
                                                elif distance(center, point) > distance(center, botRight):
                                                    botRight = point
                                            elif point[1] in range(0, center[1]):
                                                if len(topRight) == 0:
                                                    topRight = point
                                                elif distance(center, point) > distance(center, topRight):
                                                    topRight = point
                                        elif point[0] in range(0, center[0]):
                                            if point[1] in range(center[1], h):
                                                if len(botLeft) == 0:
                                                    botLeft = point
                                                elif distance(center, point) > distance(center, botLeft):
                                                    botLeft = point
                                            elif point[1] in range(0, center[1]):
                                                if len(topLeft) == 0:
                                                    topLeft = point
                                                elif distance(center, point) > distance(center, topLeft):
                                                    topLeft = point
                                    if len(topLeft) + len(topRight) + len(botRight) + len(botLeft) < 8:
                                        print "It didn't work"
                                        print topLeft, topRight, botRight, botLeft
                                        print "Couldn't final all extremes"
                                    else:
                                        cv2.circle(subImg, tuple(topLeft), 2, (255,0,0), 1)
                                        cv2.circle(subImg, tuple(topRight), 2, (0,255,0), 1)
                                        cv2.circle(subImg, tuple(botRight), 2, (0,0,255), 1)
                                        cv2.circle(subImg, tuple(botLeft), 2, (255,0,255), 1)

                                        topLeft = (topLeft[0] + x1, topLeft[1] + y1)
                                        topRight = (topRight[0] + x1, topRight[1] + y1)
                                        botRight = (botRight[0] + x1, botRight[1] + y1)
                                        botLeft = (botLeft[0] + x1, botLeft[1] + y1)


                                        imgPoints = np.array([topLeft, topRight, botRight, botLeft])
                                        srcPoints = np.array([(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0)])

                                        mat = np.array([[808, 0, 404],
                                                        [0, 608, 304],
                                                        [0, 0,   1]])

                                        print "Stuff", srcPoints.astype("float32"), imgPoints.astype("float32"), mat.astype("float32"), np.zeros((4,1)).astype("float32")
                                        rvec = np.zeros((1,3)).astype("float32")
                                        tvec = np.zeros((1,3)).astype("float32")
                                        rvec, tvec = cv2.solvePnP(srcPoints.astype("float32"), imgPoints.astype("float32"), mat.astype("float32"), np.zeros((4,1)).astype("float32"), rvec, tvec, useExtrinsicGuess=True)[-2:]
                                        '''R = cv2.Rodrigues(rvec)[0]
                                        if 0 < R[1,1] < 1:
                                                T = tvec[0,0]
                                                # If it gets here, the pose is flipped.

                                                # Flip the axes. E.g., Y axis becomes [-y0, -y1, y2].
                                                R *= np.array([
                                                        [ 1, -1,  1],
                                                        [ 1, -1,  1],
                                                        [-1,  1, -1],
                                                ])
                                                
                                                # Fixup: rotate along the plane spanned by camera's forward (Z) axis and vector to marker's position
                                                forward = np.array([0, 0, 1])
                                                tnorm = T / np.linalg.norm(T)
                                                axis = np.cross(tnorm, forward)
                                                angle = -2*math.acos(tnorm * forward)
                                                R = cv2.Rodrigues(angle * axis)[0] * R'''
                                        print "Rvec", rvec
                                        print "Tvec", tvec
                                        x = 0.0
                                        y = 0.0
                                        z = 1.0

                                        (pose, jacobian) = cv2.projectPoints(np.array([(x,y,z)]), rvec, tvec, mat.astype("float32"), None)
                                        cv2.line(img, (center[0] + x1, center[1] + y1), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 3)
                                        cv2.imshow("Sub", subImg)

                    for detection in detections:
                            loc = detection[2]
                            cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

                    self.getList.append(newDetections)
                    cv2.imshow("Vision", img)
                    key = cv2.waitKey(1)
                    self.outputVideo.write(img)
                    if key == ord('q'):
                            self.running = False
                    elif key == ord(' '):
                            continue
		#self.activeCamera.stopCapture()
                self.outputVideo.release()

	def killThread(self):
		self.running = False

if __name__ == "__main__":
	cv = yoloSimplified()
	cv.run()

