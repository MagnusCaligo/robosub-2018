#include "mechavision.hpp"
#include <vector>
#include <string>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <future>
#include <thread>
#include <dlib/threads.h>
#include <dlib/ref.h>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/features2d.hpp>
using namespace cv;
using namespace std;
using namespace FlyCapture2;


/*************
 * Use
 * 	- Contructs the mechavision class
 *
 * Parameters 
 * 	- context  --> visionworks context gaurd passed from the main function
 *
 *************/
MechaVision::MechaVision()
{
    //cap_left = VideoCapture(1);
    //cap_right = VideoCapture(2);
    error = busMgr.GetNumOfCameras(&numCameras);
    std::cout << "Number of cameras detected: " << numCameras << std::endl;
    pCameras = new Camera[numCameras];
    frame_count = 0;
    imageWriteNumber = 0;
}


/*************
 * Use
 * 	- Sets the gui parameters map. Contents of 
 * 	  the map can be seen in the computerVisionComm class.
 *
 *************/
void MechaVision::setGuiParams(GuiParameters &temp)
{
    guiParameters = temp;
    //std::cout << "Hue max: " << guiParameters["hueMax"];
}


int MechaVision::writeFrame(Mat &frame)
{
    std::vector<int> compression_params;
    compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
    compression_params.push_back(25);
	        
    cv::imwrite("/media/nvidia/Extra Space/robosub-2017/RoboSub-2017/lib/GuiComponents/ComputerVision/processed" + std::to_string(imageWriteNumber) +".png", frame, compression_params);
	imageWriteNumber++;
	if(imageWriteNumber >= 5){
		imageWriteNumber = 0;
	}
    return 1;
}

/*************
 * Use
 * 	- Write the processed frames to disk
 * 	  so that the gui process can display them
 *
 ************/
void MechaVision::writeProcessedFrames()
{
    std::vector<int> compression_params;
    compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
    compression_params.push_back(25);

    cv::imwrite("/home/nvidia/yolo_cpp/app/DetectTrackDistance/processed.jpg", left);

}

/*************
 * Use
 * 	- To apply HSV thresholding on an image based on the
 * 	  min and max HSV values
 * Returns
 * 	- Thresholded frame
 *************/
void MechaVision::HSVThresholding()
{
}




/*************
 * Use:
 * 	- Initialize dlib correlation trackers for all the detections.
 *
 ************/
void MechaVision::initTracker()
{
    // Loop through the detections vector.  Each element is a detection
    for (auto & detection: detections)
    {
	    float label = detection[0];
	    float prob = detection[1];
            float centerX = detection[2];
            float centerY = detection[3];
            float width = detection[4];
            float height = detection[5];
            //std::cout << "Tracker box:" << " " 
		    //<< label << " " << prob << " " <<
		    //centerX << " " << centerY << " " << 
		    //width << " " << height << " "  << std::endl << std::flush;
            
	    dlib::cv_image<dlib::rgb_pixel> dlib_img(tracking);
            tracker.start_track(dlib_img, dlib::centered_rect(dlib::point(centerX, centerY), width, height));

    }
}

/*************
 * Use:
 *	- Update the trackers on a new frame.
 *
 ************/
void MechaVision::updateTracker()
{
    double confidence = tracker.update(dlib_img);
    tracker_pos = tracker.get_position();

    //std::cout << "Tracker confidence: " << confidence << std::endl << std::flush;
    //std::cout << tracker_pos.left() << " " << tracker_pos.right() << " " 
    //	    << tracker_pos.top() << " " << tracker_pos.bottom() << " " << std::endl << std::flush;

    std::vector<float> box;
    box.push_back(tracker_pos.left());
    box.push_back(tracker_pos.top());
    box.push_back(tracker_pos.right());
    box.push_back(tracker_pos.bottom());

    MechaVision::drawBoundingBoxes(box);
}

/*************
 * Use
 * 	- Set Detections
 *
 ************/
void MechaVision::setDetections(std::vector<Detection> temp)
{
    detections = temp;
}


void MechaVision::encodeImage(cv::Mat frame)
{
    cv::imencode(".jpeg", frame, data);

}

std::vector<uchar> MechaVision::getEncodedData()
{
    return data;
}

/*************
 * Use
 * 	- Writes the input frames to disk so that the python
 * 	  neural network process can open these images and 
 * 	  run inference on them.
 *
 ************/
void MechaVision::writeInputFrames()
{
    std::vector<int> compression_params;
    compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
    compression_params.push_back(50);
    imwrite("/home/nvidia/robosub-2017/MechaVision/DetectTrackDistance/left.jpeg", left, compression_params);
    imwrite("/home/nvidia/robosub-2017/MechaVision/DetectTrackDistance/right.jpeg", right, compression_params);
}

cv::Mat MechaVision::drawDetections(Yolo &yolo, cv::Mat &img, std::vector<DetectedObject> &detection)
{
	for(int i = 0; i < detection.size(); i++)
	{
		DetectedObject& o = detection[i];

		cv::rectangle(img, o.bounding_box, cv::Scalar(255,0,0), 2);

		const char* class_name = yolo.getNames()[o.object_class];

		char str[255];
		sprintf(str,"%s", class_name);
		cv::putText(img, str, cv::Point2f(o.bounding_box.x,o.bounding_box.y), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0,0,255), 2);
	}

	//cv::imshow("image", img);
	return img;
}


/*************
 * Use
 * 	- Loops through the detections and calculates
 * 	  appropriate values to pass to the drawBoundingBoxes
 * 	  functions.
 * 	  	- The boxes returned by the python process
 * 	  	  are of (center X, center Y, Width, Height)
 *
 ************/
void MechaVision::drawPythonBoxes()
{
    for (auto & detection : detections)
    {
        float maxX = detection[2] + detection[4];
        float minX = detection[2] - detection[4];

        float maxY = detection[3] + detection[5];
        float minY = detection[3] - detection[5];

        std::vector<float> box;
        box.push_back(maxX);
        box.push_back(minX);
        box.push_back(maxY);
        box.push_back(minY);

        MechaVision::drawBoundingBoxes(box);
    }
}

/*************
 * Use
 * 	- Draws the bounding box onto the screen.
 *
 * Parameters
 * 	- Box  --> vector of floats containing the boxes (maxX, minX, maxY, minY)
 *
 ************/
void MechaVision::drawBoundingBoxes(std::vector<float> box)
{
    RNG rng(12345);
    Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
    rectangle(left, Point(box[1],box[3]), Point(box[0],box[2]), color, 2);
}

/*************
 * Use
 * 	- Reads a video or reads from the point grey cameras.
 * 	  If a path is given then the function will read frames
 * 	  from that path.  Otherwise the function will grab the frames
 * 	  from the point grey camera and then convert to openCV frames.
 *
 ************/
void MechaVision::getVideoCapture(std::string &video_path)
{
    if (video_path.compare("none") == 0)
    {
	//std::cout << "Using point grey cameras." << std::endl << std::flush;
	/*
	//left = MechaVision::threadVideoCapture(fl_camera);
	//right = MechaVision::threadVideoCapture(fr_camera);
	//auto videoCapFl = std::async([&MechaVision, fl_camera]{ return MechaVision::threadVideoCapture(fl_camera); });
	//auto videoCapFl = std::async(&MechaVision::threadVideoCapture, fl_camera);
	//auto videoCapFr = std::async(&MechaVision::threadVideoCapture, fr_camera);
	Image rawImage;
	Error error = fl_camera.RetrieveBuffer( &rawImage );

	Image rgbImage;
	rawImage.Convert( FlyCapture2::PIXEL_FORMAT_BGR, &rgbImage);

	unsigned int rowBytes = (double)rgbImage.GetReceivedDataSize()/(double)rgbImage.GetRows();
	cv::Mat frame = cv::Mat(rgbImage.GetRows(), rgbImage.GetCols(), CV_8UC3, rgbImage.GetData(), rowBytes);

	Image rawImage2;
	error = fr_camera.RetrieveBuffer( &rawImage );

	Image rgbImage2;
	rawImage.Convert( FlyCapture2::PIXEL_FORMAT_BGR, &rgbImage2);

	unsigned int rowBytes2 = (double)rgbImage2.GetReceivedDataSize()/(double)rgbImage2.GetRows();
	cv::Mat frame2 = cv::Mat(rgbImage2.GetRows(), rgbImage2.GetCols(), CV_8UC3, rgbImage2.GetData(), rowBytes2);
	*/

	//dlib::thread_function cap1(&(this->threadVideoCapture), dlib::ref(fl_camera), dlib::ref(temp_fl));
	auto cap1 = std::async(&MechaVision::cameraCapFl, this);
  	auto cap2 = std::async(&MechaVision::cameraCapFr, this);
	cap1.get();
	cap2.get();

	cv::cvtColor(left, drawing, CV_BGR2GRAY);
	tracking = left.clone();
	width = left.cols;
	height = left.rows;

    }
    else 
    {
	std::cout << "Not Implemented yet" << std::endl << std::flush;		

    }

}

void MechaVision::cameraCapFl()
{
    Image rawImage;

    FlyCapture2::Error error = fl_camera.RetrieveBuffer( &rawImage );

    Image rgbImage;
    rawImage.Convert( FlyCapture2::PIXEL_FORMAT_BGR, &rgbImage);

    unsigned int rowBytes = (double)rgbImage.GetReceivedDataSize()/(double)rgbImage.GetRows();
    cv::Mat frame = cv::Mat(rgbImage.GetRows(), rgbImage.GetCols(), CV_8UC3, rgbImage.GetData(), rowBytes);
    //cv::Point2f center(frame.rows/2.0F, frame.cols/2.0F);
    //cv::Mat rot_mat = cv::getRotationMatrix2D(center, 180, 1.0);
    //cv::Mat dest;
    //cv::warpAffine(frame, dest, rot_mat, frame.size());

    cv::Mat dst;

    cv::Point2f pc(frame.cols/2., frame.rows/2.);
    cv::Mat r = cv::getRotationMatrix2D(pc, -180, 1.0);

    cv::warpAffine(frame, dst, r, frame.size()); 

    left = dst.clone();
}

void MechaVision::cameraCapFr()
{   
    Image rawImage2;

    FlyCapture2::Error error = fr_camera.RetrieveBuffer( &rawImage2 );

    Image rgbImage2;
    rawImage2.Convert( FlyCapture2::PIXEL_FORMAT_BGR, &rgbImage2);

    unsigned int rowBytes2 = (double)rgbImage2.GetReceivedDataSize()/(double)rgbImage2.GetRows();
    cv::Mat frame2 = cv::Mat(rgbImage2.GetRows(), rgbImage2.GetCols(), CV_8UC3, rgbImage2.GetData(), rowBytes2);
    right = frame2.clone();
}
   

/*************
 * Use
 * 	- Reads in a single image.
 *
 * Parameters
 * 	- image_path  --> path to read from
 *
 ************/
void MechaVision::getSingleImage(std::string &image_path)
{
   left = cv::imread(image_path);
   right = left.clone();
   drawing = left.clone();
   tracking = left.clone();
   width = left.cols;
   height = left.rows;
}

Mat MechaVision::getDrawing()
{
   return drawing;
}

Mat MechaVision::getLeftFrame()
{
	//std::cout << "size: " + std::to_string(left.cols) << std::endl;
   return left;
}

/*************
 * Use
 * 	- Undistorts the class opencv frames.  After
 * 	  undistorting it converts the undistorted opencv frames
 * 	  to visionworks frames.
 *
 * Parameters
 * 	- context  --> visionworks context that NEEDS to be from the main function
 * 		       and be passed by reference
 *
 ************/


/* NOT WORKING
 * Use 
 * 	- Converts an visionworks image to opencv image.
 *
 * Parameters
 * 	- disp_cp  --> visionworks disparity image
 *
 */


cv::Mat MechaVision::getDisparity()
{
    return cv_disparity;
}

/*
 * Use
 * 	- Runs the stereo vision pipeline:
 * 	  capture and undistort --> create disparity --> run stereo matching
 *
 * Parameters
 * 	- context  --> visionworks context that NEEDS to be from the main function
 * 		       and passed by reference
 *
 */




/**************
 * Use
 * 	- Undistorts the class's opencv frames.  For more
 * 	  information see the OpenCV C++ Stereo Callibration example.
 *
 *************/
void MechaVision::undistortFrames()
{

    if (frame_count == 0)
    {
	    Size img_size = left.size();


	    /* Creating the input matrixes for the stereo rectify */
	    // M1: camera 1 matrix
	    // M2: camera 2 matrix
	    // D1: camera 1 Distortion matrix
	    // D2: camera 2 Distortion matrix
	    // R: Rotation matrix between camera 1 and 2
	    // T: Translation matrix between camera 1 and 2
	    Mat Q;
	    Mat M2 = (Mat_<double>(3,3) << 662.4004, 0, 410.5933,
					0, 653.6548, 315.9474,
					0, 0, 1);


	    //cout << "M1 = " << endl << M1 << endl << endl;

	    Mat M1 = (Mat_<double>(3,3) << 655.3211, 0, 406.2318,
					0, 646,3686, 312.3368,
					0, 0, 1);

	    Mat dm1, dm2;
	    //matMulDeriv(M1, M2, dm1, dm2);


	    //cout << "M2 = " << endl << M2 << endl << endl;


	    // (K1, K2, P1, P2, K3)
	    Mat D2 = (Mat_<double>(4,1) << -0.3516, 0.1663, 0.0020, -0.0005717);
	    //cout << "D1 = " << endl << D1 << endl << endl;

	    Mat D1 = (Mat_<double>(4,1) << -0.3361, 0.1304, 0.0022, -0.00025033);
	    //cout << "D2 = " << endl << D2 << endl << endl;


	    Mat R = (Mat_<double>(3,3) <<     0.9993,    0.0027,    0.0375,
			       -0.0028,    1.0000,    0.0018,
			          -0.0374,   -0.0019,    0.9993);
				
			
	    //cout << "R = " << endl << R << endl << endl;

	    Mat T = (Mat_<double>(3,1) <<   -97.8725,    1.1212,   -1.9711);
	    //cout << "T = " << endl << T << endl << endl;


	    /* Output object from stereo rectify */
	    // R1: Output 3x3 rectification transform for camera 1
	    // R2: Output 3x3 rectification transform for camera 2
	    // P1: Output 3x4 projection matrix in the new rectified coordinate system for camera 1
	    // P2: Output 3x4 projection matrix in the new rectified coordinate system for camera 2
	    // Q: Output 4x4 disparity-to-depth mapping matrix
	    Mat R1, P1, R2, P2;
	    stereoRectify( M1, D1, M2, D2, img_size, R, T, R1, R2, P1, P2, Q, CALIB_ZERO_DISPARITY, -1, img_size );

	    /* Create recitfy maps */
	    initUndistortRectifyMap( M1, D1, R1, P1, img_size, CV_16SC2, map11, map12);

	    initUndistortRectifyMap( M2, D2, R2, P2, img_size, CV_16SC2, map21, map22);
	    frame_count = 0;
    }
    else
    {
	    /* Remap images */
	    Mat temp1, temp2;
	    remap(left, temp1, map11, map12, INTER_LINEAR);

	    remap(right, temp2, map21, map22, INTER_LINEAR);
	    left = temp1;
	    right = temp2;
    }
}

/*************
 * Use
 * 	- Initializing the point grey cameras to start
 * 	  capturing.
 *
 ************/
int MechaVision::initCameras()
{

// Prepare each camera to acquire images
//
// *** NOTES ***
// For pseudo-simultaneous streaming, each camera is prepared as if it
// were just one, but in a loop. Notice that cameras are selected with
// an index. We demonstrate pseduo-simultaneous streaming because true
// simultaneous streaming would require multiple process or threads,
// which is too complex for an example.
//
//
	CameraInfo camInfo;
	BusManager busMgr;
	PGRGuid guid;

	error = busMgr.GetCameraFromIndex(0, &guid);	
	error = fl_camera.Connect( &guid );
	error = fl_camera.GetCameraInfo( &camInfo );
	error = fl_camera.StartCapture();
	if ( error != PGRERROR_OK)
	{
	    std::cout << "Failed to start image capture.1" << std::endl << std::flush;
	}
/*
	error = busMgr.GetCameraFromIndex(1, &guid);
	error = fr_camera.Connect( &guid );
	error = fr_camera.GetCameraInfo( &camInfo );
	error = fr_camera.StartCapture();
	if ( error != PGRERROR_OK)
	{
	    std::cout << "Failed to start image capture.2" << std::endl << std::flush;
	}*/

	return 1;

}


