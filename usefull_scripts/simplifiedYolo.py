onLinux = True
import math
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
            self.rvec = np.zeros((1,3)).astype("float32")
            self.tvec = np.zeros((1,3)).astype("float32")

            self.useVideo = False
            self.videoPath = "Downloads/example3.mp4"

	    self.usePicture = False
            self.pictureId = 3227
	    self.picturePath = "darknet/allLabeledImages/" + str(self.pictureId) + ".jpg"
	    self.picturePathSrc = "darknet/allLabeledImages/"

            self.activeCamera = None

            #Top left hole, TR hole, Bottom Hole, cherry, banana, grape, TLH TRC, TLH BRC, TLH BLC, TLH TLC, ....

            self.torpedoDictionary = {"Top Left Hole":0, "Top Right Hole":1, "Bottom Hole":2}#, "Cherry":3, "Banana":4, "Grape":5, "TLHTRC":5,"TLHBRC":6,"TLHBLC":7,"TLHTLC":8 } 

            self.camMat = [[808, 0, 404],
                           [0, 608, 304],
                           [0,   0, 1]]

            dn.set_gpu(0)
            self.fourcc = cv2.cv.FOURCC(*"H264")
            self.outputVideo = cv2.VideoWriter("output.avi", self.fourcc, 1, (808, 608))
            cv2.namedWindow("Vision")

            def nothing(x):
                pass
            cv2.createTrackbar("H Red Min", "Vision", 90, 255, nothing)
            cv2.createTrackbar("H Red Max", "Vision", 255, 255,nothing)
            cv2.createTrackbar("H Yel Min", "Vision", 40, 255,nothing)
            cv2.createTrackbar("H Yel Max", "Vision", 90, 255,nothing)


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
                    print "using image at location", self.picturePath
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
                        img = cv2.imread(self.picturePath)
                    #yoloImage = dn.IMAGE()
		    h,w, c = img.shape
                    detections = dn.detect_np(self.net, self.meta, img, thresh=.1, hier_thresh = .1)
                    newDetections = []
		    grape = []
		    banana = []
	 	    cherry = []
                    corners = []
                    print "=================="
                    for detection in detections:
                            fixedClassNumber = self.detectionDictionary[detection[0]]
                            newDetections.append([fixedClassNumber, detection[1], detection[2]])
			    if detection[0] == "Grape":
				grape = detection[2]
			    elif detection[0] == "Banana":
				banana = detection[2]
			    elif detection[0] == "Cherry":
				cherry = detection[2]
                            if detection[0] in ["Top Left Hole", "Top Right Hole", "Bottom Hole"]:
                                print "Drawing...."
                                error = 20
                                x1 = int(detection[2][0] - (.5 * detection[2][2])) - error
                                x2 = int(detection[2][0] + (.5 * detection[2][2])) + error
                                y1 = int(detection[2][1] - (.5 * detection[2][3])) - error
                                y2 = int(detection[2][1] + (.5 * detection[2][3])) + error
                                h,w, c = img.shape
                                if x1 < 0:
                                    x1 = 0
                                if y1 < 0:
                                    y1 = 0
                                if x2 >= w:
                                    x2 = w -1
                                if y2 >= h:
                                    y2 = h -1
                                if y2 < y1:
                                    t = y2
                                    y2 = y1
                                    y1 = t
                                if x2 < x1:
                                    t = x2
                                    x2 = x1
                                    x1 = t
                                subImg = copy.copy(img[y1:y2, x1:x2])
                                if np.prod(subImg.shape) == 0:
                                    continue
                                res = cv2.cvtColor(subImg, cv2.COLOR_RGB2HSV)
                                #kernel = np.ones((5,4), np.float32)/25
                                #binImg = cv2.filter2D(res, -1, kernel)

                                
                                print "Value.............", int(cv2.getTrackbarPos("H Red Min", "Vision"))
                                mask1 = cv2.inRange(res, np.array([int(cv2.getTrackbarPos("H Red Min", "Vision")), 0,0]), np.array([int(cv2.getTrackbarPos("H Red Max", "Vision")),255,255]))
                                mask2 = cv2.inRange(res, np.array([int(cv2.getTrackbarPos("H Yel Min", "Vision")), 0,0]), np.array([int(cv2.getTrackbarPos("H Yel Max", "Vision")),255,255]))
                                mask = cv2.bitwise_or(mask1,mask2)
                                binImg = cv2.bitwise_or(subImg, subImg, mask=mask)
                                cv2.imshow("Binary", binImg)

                                cannyImg = cv2.Canny(binImg, 00, 700, 3)
                                #subImg = copy.copy(cannyImg)
                                cv2.imshow("Canny", cannyImg)
                                h,w = subImg.shape[:2]
                                center = (w/2, h/2)
                                pose = [[[center[0], center[1]]]]
                                cv2.circle(subImg, center, 4, (255,255,0), -1)

                                contours, hierarchy = cv2.findContours(cannyImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                allConts = copy.copy(subImg)
                                cv2.drawContours(allConts, contours, -1, (0,255,0), 1)
                                cv2.imshow("All Contours", allConts)
                                if len(contours) == 0:
                                    print "NO CONTOURS"
                                if len(contours) > 0:
                                    app = contours[0]
                                    largestArea = 0
                                    for cont in contours:
                                        a = cv2.contourArea(cont)
                                        if a > largestArea:
                                            app = cont
                                            largestArea = a


                                    val = .00
                                    epsilon = val * cv2.arcLength(app, True)
                                    app = cv2.approxPolyDP(app, epsilon, True)
                                    app = [app]
                                    cv2.drawContours(subImg, app, -1, (0,255,0), 1)
                                    cv2.imshow("Sub", subImg)

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
                                        corners.append(np.insert(imgPoints, 0, (center[0] + x1, center[1] + y1, 0)))
                                        srcPoints = np.array([(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0)])

                                        mat = np.array([[808, 0, 404],
                                                        [0, 608, 304],
                                                        [0, 0,   1]])


					print "Rvec", self.rvec
					if self.rvec.shape == (1,3):
						if abs(math.degrees(self.rvec[0][1])) > 50:
						    self.rvec[0][0] = 0.0
						    self.rvec[0][1] = 0.0
						    self.rvec[0][2] = 0.0
                                        self.rvec, self.tvec = cv2.solvePnP(srcPoints.astype("float32"), imgPoints.astype("float32"), mat.astype("float32"), np.zeros((4,1)).astype("float32"), self.rvec, self.tvec, useExtrinsicGuess=True)[-2:]
                                        #self.rvec[0][0] = 0.0
                                        #self.rvec[0][2] = 0.0
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
                                        x = 0.0
                                        y = 0.0
                                        z = 2.0

                                        (pose, jacobian) = cv2.projectPoints(np.array([(x,y,z)]), self.rvec, self.tvec, mat.astype("float32"), None)
                                        cv2.line(img, (center[0] + x1, center[1] + y1), (int(pose[0][0][0]), int(pose[0][0][1])), (255,0,0), 3)
                            #cv2.waitKey(-1)

                    for detection in detections:
                            loc = detection[2]
                            if detection[0] in ["Top Left Hole", "Top Right Hole", "Bottom Hole"]:
                                cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,255,0))
                            else:
                                cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))

		    if len(banana) != 0:
			newAr = [(banana[0], banana[1], 1)] 
			corners.append(newAr)
		    if len(cherry) != 0:
			newAr = [(cherry[0], cherry[1], 2)]
			corners.append(newAr)
		    if len(grape) != 0:
			newAr = [(grape[0], grape[1], 3)]
			corners.append(newAr)

                    if len(corners) >= 3:
			print "Corners:", corners
                        topLeft = []
                        topRight = []
                        bot = []
                        center = [0,0]
                        for c in corners:
			    print "Corner is", c
			    if type(c[0]) == tuple:
				print "its a tuple"
				center[0] += c[0][0]
				center[1] += c[0][1]
			    else:
				center[0] += c[0]
				center[1] += c[1]
                        center[0] /= float(len(corners))
                        center[0] = int(center[0])
                        center[1] /= float(len(corners))
                        center[1] = int(center[1])
                        cv2.circle(img, tuple(center), 4, (0,0,0), -1)

			srcPoints = []
			imgPoints = np.array([])

                        for c in corners:
			    if c[0][2] == 0:
				    if c[0][1] in  range(0, center[1]):
					if c[0][0] in range(0, center[0]) and len(topLeft) == 0:
					    print "Top Left", c
					    topLeft = c[1:]
					    srcPoints = srcPoints + [(-8.5, -20.75,0), (-2.75, -20.75, 0), (-2.75, -13, 0), (-8.5, -13, 0)]
					elif len(topRight) == 0:
					    topRight= c[1:]
					    srcPoints = srcPoints + [(2, -19.75, 0), (7.75, -19.75, 0), (7.75, -14.125, 0), (2, -14.125, 0)]
				    elif len(bot) == 0:
					    bot = c[1:]
					    srcPoints = srcPoints + [(-4.5, 13.25,0), (3.5, 13.25,0), (3.5, 21, 0), (-4.25, 21, 0)]
			    	    imgPoints = np.concatenate((imgPoints, c[1:]))
			    elif c[0][2] in [1,2,3]:
				if c[0][2] == 1:
					srcPoints = srcPoints + [(7, -4)]
				elif c[0][2] == 2:
					srcPoints = srcPoints + [(-9, -4)]
				elif c[0][2] == 3:
					srcPoints = srcPoints + [(-3, -4)]
			        imgPoints = np.concatenate((imgPoints, (c[0][0], c[0][1])))

			if len(srcPoints) > 8:
                            srcPoints = np.array(srcPoints)
                            '''imgPoints = imgPoints.tolist()
                            for i,v in enumerate(imgPoints):
                                imgPoints[i] = (v[0], v[1])
                            imgPoints = np.array(imgPoints)
                            print imgPoints'''
                            print type(imgPoints), type(srcPoints), type(np.array(self.camMat))
                            rvec, tvec = cv2.solvePnP(srcPoints.astype("float32"), imgPoints.astype("float32"), np.array(self.camMat).astype("float32"), np.zeros((4,1)).astype("float32"))[-2:]
                            print "Board rvec and tvec........................."
                            print rvec, "Degrees:", math.degrees(rvec[1][0]), "\n"
                            print tvec
                            (pose, jacobian) = cv2.projectPoints(np.array([(0.0,0.0,2)]), rvec, tvec, np.array(self.camMat).astype("float32"), None)
                            cv2.line(img, (center[0], center[1]), (int(pose[0][0][0]), int(pose[0][0][1])), (0,92,255), 3)




                    self.getList.append(newDetections)
                    cv2.imshow("Vision", img)
                    key = cv2.waitKey(1)
                    self.outputVideo.write(img)
                    if key == ord('q'):
                        self.running = False
                    elif key == ord(' '):
                        if self.usePicture == True:
                            self.pictureId += 1
                            if self.pictureId >= 3347:
                                self.running = False
                            self.picturePath = self.picturePathSrc + str(self.pictureId) + ".jpg"
                            print "New path", self.picturePath
                        continue
                    elif key == ord('s'):
                        cv2.imwrite("output.png", img)
		#self.activeCamera.stopCapture()
                self.outputVideo.release()

	def killThread(self):
		self.running = False

if __name__ == "__main__":
	cv = yoloSimplified()
	cv.run()

