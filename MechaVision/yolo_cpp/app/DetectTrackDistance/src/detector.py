from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import time
import sys
import os
import glob

import numpy as np
import tensorflow as tf
import cv2

from config import *
from train import _draw_box
from nets import *


class Detector:
    def __init__(self):
        self.model = None
        self.mc = None
        self.saver = None
	self.count = 0
	self.sess = None
        self.final_boxes = []
        self.final_class = []
        self.final_probs = []

    def getFinalBoxes(self):
        return self.final_boxes

    def getFinalClass(self):
        return self.final_class

    def getFinalProbs(self):
        return self.final_probs

    def runModel(self):
        """Detect image."""
        with tf.Graph().as_default():
            if self.count == 0:
		self.count = 1
                # Load model
                self.mc = kitti_squeezeDet_config()
                self.mc.BATCH_SIZE = 1
                # model parameters will be restored from checkpoint
                self.mc.LOAD_PRETRAINED_MODEL = False
                self.model = SqueezeDet(self.mc, 0)
                self.saver = tf.train.Saver(self.model.model_params)
                self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
		print("Loaded Model")
	        self.saver.restore(self.sess, '/home/ubuntu/Workspace/DetectTrackDistance/src/squeezeDet/data/model_checkpoints/squeezeDet/model.ckpt-87000')
            else:
                for f in glob.iglob('/home/ubuntu/Workspace/DetectTrackDistance/left.jpg'):
                    im = cv2.imread(f)
                    im = im.astype(np.float32, copy=False)
                    im = cv2.resize(im, (self.mc.IMAGE_WIDTH, self.mc.IMAGE_HEIGHT))
                    input_image = im - self.mc.BGR_MEANS

                    # Detect
                    det_boxes, det_probs, det_class = self.sess.run(
                        [self.model.det_boxes, self.model.det_probs, self.model.det_class],
                        feed_dict={self.model.image_input: [input_image], self.model.keep_prob: 1.0})

                    # Filter
                    final_boxes, final_probs, final_class = self.model.filter_prediction(
                        det_boxes[0], det_probs[0], det_class[0])

                    keep_idx = [idx for idx in range(len(final_probs)) \
                                if final_probs[idx] > self.mc.PLOT_PROB_THRESH]
                    self.final_boxes = [final_boxes[idx] for idx in keep_idx]
                    self.final_probs = [final_probs[idx] for idx in keep_idx]
                    self.final_class = [final_class[idx] for idx in keep_idx]

                    if self.final_boxes == []:
                        self.final_boxes.append(-1)
                    else:
                        self.final_boxes = self.final_boxes[0].astype(float).tolist()
                    if self.final_class == []:
                        self.final_class.append(-1)
                    if self.final_probs == []:
                        self.final_probs.append(-1)
                    else:
                        self.final_probs = map(float, self.final_probs)

		    final_dict = {'final_boxes': self.final_boxes, 'final_probs': self.final_probs, 'final_class': self.final_class}
                    print (final_dict)
                    return final_dict

'''
detector = Detector()
detector.runModel()
detector.runModel()
print (detector.final_boxes)
print (detector.final_class)
print (detector.final_probs)
'''
