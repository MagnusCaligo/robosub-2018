import darknet as dn
import sys
import os
import PyCapture2 as pc2
import cv2
import numpy as np
import time

dn.set_gpu(0)

net = dn.load_net("6_15_test.cfg", "6_15_test_40000.weights", 0)
meta = dn.load_meta("test.data")

bus = pc2.BusManager()
cam = pc2.Camera()
cam.connect(bus.getCameraFromIndex(0))
cam.startCapture()
startTime = time.time()

while True:
	print "Time was", time.time() - startTime
	startTime = time.time()
	image = cam.retrieveBuffer()
	image = image.convert(pc2.PIXEL_FORMAT.BGR)
	img = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols(), 3))
	yoloImage = dn.IMAGE()
	detections = dn.detect_np(net, meta, img)
	for detection in detections:
		loc = detection[2]
		cv2.rectangle(img, (int(loc[0]-(.5 * loc[2])), int(loc[1]- (.5 * loc[3]))), (int(loc[0] + (.5*loc[2])), int(loc[1] + (.5*loc[3]))), (0,0,255))
	cv2.imshow("Test", img)
	key = cv2.waitKey(1)
	if key == ord("q"):
		break


