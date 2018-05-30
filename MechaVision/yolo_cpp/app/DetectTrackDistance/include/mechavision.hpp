#ifndef __MECHAVISION_HPP__
#define __MECHAVISION_HPP__

#include "opencv2/opencv.hpp"
#include <string>
#include <iomanip>
#include <memory>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <vector>
#include <mutex>
#include <stdlib.h>
#include <thread>
#include <time.h>
#include <stdio.h>

#include <zmq.hpp>
#include <iostream>

/*#include <dlib/image_processing.h>
#include <dlib/threads.h>
#include <dlib/ref.h>
#include <dlib/dnn.h>
#include <dlib/data_io.h>
#include <dlib/image_processing.h>
#include <dlib/image_transforms.h>
#include <dlib/gui_widgets.h>
#include <dlib/opencv.h>
#include <dlib/gui_widgets.h>
#include <opencv2/imgproc/imgproc.hpp>
//#include <dlib/geometry.h>*/

#include "FlyCapture2.h"

#include "computerVisionComm.hpp"
#include "stereo_matching.hpp"
#include <yolo.h>

using namespace FlyCapture2;

struct Tracker {
	std::vector<float> tracker_pos;
	//dlib::correlation_tracker tracker;
	//dlib::drectangle dlib_tracker_pos;
};


class MechaVision
{
public:
    MechaVision();

    void getVideoCapture(std::string &);
    void getSingleImage(std::string &);
    void undistortFrames();
    void releaseVXImages();
    bool zmqMessages(zmq::context_t&, zmq::socket_t&);
    bool getParams(zmq::context_t&, zmq::socket_t&);
    cv::Mat getLeftFrame();
    void writeInputFrames();
    int writeFrame(cv::Mat &frame);
    int imageWriteNumber;
    int initCameras();
    void writeProcessedFrames();

    void encodeImage(cv::Mat );
    std::vector<uchar> getEncodedData();
    void cameraCapFl();
    void cameraCapFr();

    // Deal with Obstacles struct
    void drawBoundingBoxes(std::vector<float>);
    void initTracker();
    void drawPythonBoxes();
    void updateTracker();
    cv::Mat drawDetections(Yolo &, cv::Mat &, std::vector<DetectedObject> &);

    // Setters and getters
    void setDetections(std::vector<Detection> );
    void setGuiParams(GuiParameters &);
    void printDetections();
    cv::Mat getDrawing();
    cv::Mat getDisparity();

    // Getting distance to obstacle
    std::vector<float> calculateObstacleDistance();
    std::vector<float> calculateObstaclePose();

    // Image process
    void cannyEdge();
    void HSVThresholding();
    void HSIThresholding();
    void getContours();


private:
    void sendMessage(zmq::socket_t &, std::string);
    bool check();
    std::shared_ptr<ComputerVisionComm> computerVisionComm;
    GuiParameters guiParameters;

    // Image variables
    int width, height;

    // Encoded images
    std::vector<uchar> data;


    // OpenCV variables
    cv::Mat drawing, left, right, cv_disparity, tracking;
    cv::VideoCapture cap_left, cap_right;
    cv::Mat map11, map12, map21, map22;
    int frame_count;
    //cv::gpu::GpuMat gpu_left, gpu_right, gpu_disparity;

    // Dlib variables
    /*dlib::correlation_tracker tracker;
    dlib::matrix<dlib::rgb_pixel> dlib_img;
    dlib::drectangle tracker_pos;*/

    // PointGrey Variables
    Error error;
    BusManager busMgr;
    unsigned int numCameras;
    Camera *pCameras;
    Camera fl_camera, fr_camera, bl_camera, br_camera;

    // Obstacles struct
    std::vector<Detection> detections;
    std::vector<Tracker> trackers;

    // Parameters for fast
    int fast_type;
    int fast_thresh;
};


#endif
