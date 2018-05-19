"""
SqueezeDet from a webcam.
"""

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

from config import *
from train import _draw_box
from nets import *

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string(
    'mode', 'image', """'image' or 'video'.""")
tf.app.flags.DEFINE_string(
    'checkpoint', './data/model_checkpoints/squeezeDet/model.ckpt-87000',
    """Path to the model parameter file.""")
tf.app.flags.DEFINE_string(
    'input_path', './data/sample.png',
    """Input image or video to be detected. Can process glob input such as """
    """./data/00000*.png.""")
tf.app.flags.DEFINE_string(
    'out_dir', './data/out/', """Directory to dump output image or video.""")


def webcam():
    """
    Detect in a webcam
    :return:
    """
    with tf.Graph().as_default():
        # Load model
        mc = kitti_squeezeDet_config()
        mc.BATCH_SIZE = 1 
        mc.LOAD_PRETRAINED_MODEL = False
        model = SqueezeDet(mc, FLAGS.gpu)

        saver = tf.train.Saver(model.model_params)

        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            saver.restore(sess, FLAGS.checkpoint)

            times = {}
            count = 0
            cap = cv2.VideoCapture(1)

            while (True):
                t_start = time.time()
                count += 1

                ret, frame = cap.read()

                if ret==True:
                    # crop frames
                    #frame = frame[500:-205, 239:-439, :]
                    # Resize image to 375x1242
                    #dim = (1242, 375)
                    #frame = cv2.resize(frame, dim)
                    im_input = frame.astype(np.float32) - mc.BGR_MEANS
                else:
                    break


                t_reshape = time.time()
                times['reshape'] = t_reshape - t_start

                det_boxes, det_probs, det_class = sess.run(
                    [model.det_boxes, model.det_probs, model.det_class],
                    feed_dict={model.image_input: [im_input], model.keep_prob: 1.0})

                t_detect = time.time()
                times['detect'] = t_detect - t_reshape

                # Filter
                final_boxes, final_probs, final_class = model.filter_prediction(
                    det_boxes[0], det_probs[0], det_class[0])

                keep_idx = [idx for idx in range(len(final_probs)) \
                            if final_probs[idx] > mc.PLOT_PROB_THRESH]
                final_boxes = [final_boxes[idx] for idx in keep_idx]
                final_probs = [final_probs[idx] for idx in keep_idx]
                final_class = [final_class[idx] for idx in keep_idx]

                t_filter = time.time()
                times['filter'] = t_filter - t_detect

                # TODO(bichen): move this color dict to configuration file
                cls2clr = {
                    'car': (255, 191, 0),
                    'cyclist': (0, 191, 255),
                    'pedestrian': (255, 0, 191)
                }
                _draw_box(
                    frame, final_boxes,
                    [mc.CLASS_NAMES[idx] + ': (%.2f)' % prob \
                     for idx, prob in zip(final_class, final_probs)],
                    cdict=cls2clr
                )

                t_draw = time.time()
                times['draw'] = t_draw - t_filter

                cv2.imshow('Frame', frame)

                times['total'] = time.time() - t_start

                # time_str = ''
                # for t in times:
                #   time_str += '{} time: {:.4f} '.format(t[0], t[1])
                # time_str += '\n'
                time_str = 'Total time: {:.4f}, detection time: {:.4f}, filter time: ' \
                           '{:.4f}'. \
                    format(times['total'], times['detect'], times['filter'])

                print(time_str)
                if cv2.waitKey(1) == 27:
                    break
            cv2.destroyAllWindows()

def main():
    webcam()

if __name__ == '__main__':
    main()
