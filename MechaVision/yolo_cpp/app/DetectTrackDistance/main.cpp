#include "opencv2/opencv.hpp"
#include <iostream>
#include <string>
#include <iomanip>
#include <memory>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <zmq.hpp>
#include <thread>
#include <future>
#include <functional>
#include <ctime>
#include <yolo.h>
#include "mechavision.hpp"
#include "computerVisionComm.hpp"
#include "color_disparity_graph.hpp"

using namespace cv;

const int frameSkip = 0;
int writeFrameSkip = 0;
bool STATE_LOOKING = true;
bool STATE_TRACKING = false;


std::vector<DetectedObject> detect(std::shared_ptr<MechaVision> &mechaVision, Yolo &yolo, cv::Mat &img){

	std::vector<DetectedObject> detection;
	//img = mechaVision->getLeftFrame();
	yolo.detect(img, detection);

	return detection;
}


int main( int argc, char** argv)
{
    try
    {  
        // Socket Initialization
	zmq::context_t zmq_context(1);
	zmq::socket_t socket(zmq_context, ZMQ_REP);
	socket.bind("tcp://*:1234");
	std::shared_ptr<ComputerVisionComm> computerVisionComm;
	GuiParameters guiParameters;

        // Initialize mechaVision, render, and disparity image
	std::shared_ptr<MechaVision> mechaVision(new MechaVision());
        int x = mechaVision->initCameras();

	Mat left_frame, drawing_frame;
        //std::unique_ptr<nvxio::Render> render(
        //           nvxio::createDefaultRender(context, "Basic tutorial", 808, 608));

	double proc_ms = 0;


	bool startTracking = false;
	std::string none = "none";
        int frameCount = 0;
	        /*
		 *
		 * videoCapture-> write frames -> run neural network model -> stereo vision -> display left frame
		 *                  -> four threads   -> two threads to read     -> bring in next image
		 *                                                                     -> batch size two
		 *                                                                                       */

	Yolo yolo;
	yolo.setConfigFilePath("/media/nvidia/Extra\ Space/robosub-2017/MechaVision/yolo_cpp/app/DetectTrackDistance/cfg/yolo-allObstacles.cfg");
	yolo.setDataFilePath("/media/nvidia/Extra\ Space/robosub-2017/MechaVision/yolo_cpp/app/DetectTrackDistance/data/allObstacles.data");
	yolo.setWeightFilePath("/media/nvidia/Extra\ Space/yolo-allObstacles_8000.weights");
	yolo.setAlphabetPath("/media/nvidia/Extra\ Space/home/ubuntu/robosub-2017/MechaVision/yolo_cpp/app/DetectTrackDistance/data/labels/");
	yolo.setNameListFile("/media/nvidia/Extra\ Space/robosub-2017/MechaVision/yolo_cpp/app/DetectTrackDistance/data/allObstacles.names");

	Mat img;
	Mat rawImg;
        int frameSkip = 0;
	std::clock_t start;
	std::clock_t program_start;
	std::cout << "Starting main loop..." << std::endl;
	std::vector<DetectedObject> detections;
	for (;;)
	{

		//std::cout << "Test" << std::endl;
	     /******************************************
	      *               GUI COMM
	      *
	      *****************************************/
	     start = std::clock();
	     program_start = std::clock();
	     //guiParameters = computerVisionComm->getMessage(zmq_context, socket);
	     //mechaVision->setGuiParams(guiParameters);
	     
	     //std::cout << "Get Message" << std::endl;

	     
	     /*if (guiParameters["useImage"].compare("true") == 0)
			mechaVision->getSingleImage(guiParameters["imagePath"]);
	     else if (guiParameters["useVideo"].compare("true") == 0)
			mechaVision->getVideoCapture(guiParameters["videoPath"]);

	     else if (guiParameters["useCameras"].compare("true") == 0)*/
			mechaVision->getVideoCapture(none);

		frameSkip = 0;/*
		if(guiParameters["frameSkip"].compare("UTF-8") != 0){
			//std::cout << "frameSkip value: " + guiParameters["frameSkip"] << std::endl;
			frameSkip = std::stoi(guiParameters["frameSkip"]);
		}*/
		
		//std::cout << "Test 1" << std::endl;

	     //std::cout << "Parameters Time: " << (std::clock() - start) / (double)(CLOCKS_PER_SEC /1000) << " ms " << std::endl << std::flush;

	     /*******************************************
	      *            DECTECTION & STEREO
	      *
	      ******************************************/ 
	     // If looking state then we run detection
	     // on every frame
	     // If tracking state then we run tracking
	     // on every skipped frame and detection when
	     // the frame count is equal to frame skip.
	     
	     start = std::clock();
	     
		mechaVision->undistortFrames();	     
	     img = mechaVision->getLeftFrame();
	     rawImg = img.clone();
		
	     //cv::Size size(288, 288);
	     //cv::resize(img, img, size);
	     //cv::imshow("left", img); // If error here then that means we aren't getting the frame
	     //cv::imshow("left", img); // If error here then that means we aren't getting the frame
             //vx_image disparity = vxCreateImage(context, 808, 608, VX_DF_IMAGE_U8);
	     //vx_image color_disp = vxCreateImage(context, 808, 608, VX_DF_IMAGE_RGB);
	     mechaVision->drawDetections(yolo,img, detections); 
	     //auto td_draw = std::async([&]{mechaVision->drawDetections(yolo, img, detections);});
	     //td_draw.get();
	     
	     cv::imshow("left", img);
		cv::waitKey(1);
	     
	     if(writeFrameSkip >= 1){
		//	auto td_write = std::async([&]{mechaVision->writeFrame(img);});
		//	td_write.get();
			writeFrameSkip = 0;
		}
	writeFrameSkip++;
	     
		//std::cout << "Test 2" << std::endl;


	     if (true || (STATE_LOOKING && frameCount >= frameSkip)){  // Looking for obstacles{

			//std::cout << "Before: " << (std::clock() - start) / (double)(CLOCKS_PER_SEC /1000) << " ms " << std::endl << std::flush;
			detections = detect(std::ref(mechaVision), std::ref(yolo), std::ref(rawImg));
			//auto td_detect = std::async(detect, std::ref(mechaVision), std::ref(yolo), std::ref(rawImg));
			//detections = detect(std::ref(mechaVision), std::ref(yolo), std::ref(img));
			//auto td_stereo = std::async(stereoVision, std::ref(mechaVision), std::ref(context), std::ref(disparity), std::ref(color_disp));   

			//cv::Mat fast_img = mechaVision->fastFeaturesDetections(img);
			//detections = td_detect.get();
			
			
			//std::cout << "Test 3" << std::endl;

			//disparity = td_stereo.get();
			//render->putImage(disparity);

			//std::cout << "After " << (std::clock() - start) / (double)(CLOCKS_PER_SEC /1000) << " ms " << std::endl << std::flush;

			//vxReleaseImage(&disparity);
			//vxReleaseImage(&color_disp);

			
			
			frameCount = 0;
			//cv::imshow("keypoints", fast_img);

	    }
		if (detections.size() > 0){
			std::cout << "Yay!" << std::endl;
			Json::Value value;
			Json::StyledWriter writer;
			
			int size = detections.size();
			int classNumber[size];
			int xLocation[size];
			int yLocation[size];
			int width[size];
			int height[size];
			
			value["classNumbers"];
			value["xLocations"];
			value["yLocations"];
			value["widths"];
			value["heights"];
			
			
			for(int i = 0; i < size; i++){
				value["classNumbers"].append(detections[i].object_class);
				value["xLocations"].append(detections[i].bounding_box.x);
				value["yLocations"].append(detections[i].bounding_box.y);
				value["widths"].append(detections[i].bounding_box.width);
				value["heights"].append(detections[i].bounding_box.height);
			}
			
			value["numberOfDetections"] = size;
			 
			std::string outputString = writer.write(value);
			
//			computerVisionComm->sendResponse(zmq_context, socket, outputString);
		}else{
	std::cout << "Couldn't find anything" << std::endl;
//			computerVisionComm->sendResponse(zmq_context, socket, "No Detections");
		}

		/*if (detections.size() >= 5 && false)  //I added the false because I want to keep this function here as a reference but I didn't want to comment it out
		{
			//std::cout << "Detecting something" <<std::endl;

			//vector<DetectedObject> bestDetections;
			bestDetections.push_back(DetectedObject(-1, 0
			for(DetectedObject o : detections){
				
			}
			cv::Rect roi(img.cols/2.0f, img.rows/2.0f, 0,0);
			for(DetectedObject o: detections){
				if(o.object_class == 1){
					roi = o.bounding_box;					
				}

			}
			

			DetectedObject topL(-1, 0, cv::Rect(roi.x + (roi.width/2.0f),roi.y + (roi.height/2.0f),0,0));
			DetectedObject topR(-1, 0, cv::Rect(roi.x + (roi.width/2.0f),roi.y + (roi.height/2.0f),0,0));
			DetectedObject botR(-1, 0, cv::Rect(roi.x + (roi.width/2.0f),roi.y + (roi.height/2.0f),0,0));
			DetectedObject botL(-1, 0, cv::Rect(roi.x + (roi.width/2.0f),roi.y + (roi.height/2.0f),0,0));

			for(DetectedObject o : detections){
				if(o.object_class == 1){continue;} //Ignore the bounding box of full board

				if(o.bounding_box.x <= topL.bounding_box.x && o.bounding_box.y >= topL.bounding_box.y)
					topL = o;
				if(o.bounding_box.x >= topR.bounding_box.x && o.bounding_box.y >= topL.bounding_box.y)
					topR = o;
				if(o.bounding_box.x <= botL.bounding_box.x && o.bounding_box.y <= botL.bounding_box.y)
					botL = o;
				if(o.bounding_box.x >= botR.bounding_box.x && o.bounding_box.y <= botR.bounding_box.y)
					botR = o;
			
			}

			vector<cv::Point3d> src_pts;
			src_pts.push_back(cv::Point3d(0.0f, 0.0f, 0.0f));
			src_pts.push_back(cv::Point3d(0.0f, 250.0f, 0.0f));
			src_pts.push_back(cv::Point3d(-275.0f, 250.0f, 0.0f));
			src_pts.push_back(cv::Point3d(-275.0f, 0.0f, 0.0f));

			vector<cv::Point2d> img_pts;
			img_pts.push_back(cv::Point2d(topL.bounding_box.x + (topL.bounding_box.width/2),topL.bounding_box.y + (topL.bounding_box.height/2)));
			img_pts.push_back(cv::Point2d(topR.bounding_box.x + (topR.bounding_box.width/2),topR.bounding_box.y + (topR.bounding_box.height/2)));
			img_pts.push_back(cv::Point2d(botR.bounding_box.x + (botR.bounding_box.width/2),botR.bounding_box.y + (botR.bounding_box.height/2)));
			img_pts.push_back(cv::Point2d(botL.bounding_box.x + (botL.bounding_box.width/2),botL.bounding_box.y + (botL.bounding_box.height/2)));


			double focal_length = img.cols; // Approximate focal length.
		    	Point2d center = cv::Point2d(img.cols/2,img.rows/2);
		   	cv::Mat camera_matrix = (cv::Mat_<double>(3,3) << focal_length, 0, center.x, 0 , focal_length, center.y, 0, 0, 1);
		    	cv::Mat dist_coeffs = cv::Mat::zeros(4,1,cv::DataType<double>::type);

			cv::Mat rotation_vector; // Rotation in axis-angle form
		    	cv::Mat translation_vector;
		     
		    	// Solve for pose
		    	cv::solvePnP(src_pts, img_pts, camera_matrix, dist_coeffs, rotation_vector, translation_vector);

			vector<Point3d> center_offset_3d;
			vector<Point2d> center_offset_2d;
			center_offset_3d.push_back(Point3d(-150.0f,125.0f,0.0));

			projectPoints(center_offset_3d, rotation_vector, translation_vector, camera_matrix, dist_coeffs, center_offset_2d);

			vector<Point3d> center3D;
			vector<Point2d> center2D;
			center3D.push_back(Point3d(-150.0f, 125.0f, 100.0f));
			projectPoints(center3D, rotation_vector, translation_vector, camera_matrix, dist_coeffs, center2D);

			

			cv::line(img,center2D[0], center_offset_2d[0], cv::Scalar(255,0,0), 5);

			auto td_draw = std::async([&]{mechaVision->drawDetections(yolo, img, detections);});
			td_draw.get();
		
	
			//STATE_LOOKING = false;
			//STATE_TRACKING = true;
		}*/
		//std::cout << "Detection and Stereo Time: " << (std::clock() - start) / (double)(CLOCKS_PER_SEC /1000) << " ms " << std::endl << std::flush;
		 /*if (!render->flush()){
			fflush(stdout);
			break;
		 }*/
		//	std::cout << "Test 4" << std::endl;
		 //if(waitKey(1) >= 0){ break; std::cout << "Test 5" << std::endl;}
		 //std::cout << "Test 6" << std::endl;

		 /******************************************
		  *               GUI COMM
		  *
		  *****************************************/
		 //computerVisionComm->sendResponse(zmq_context, socket, "processed");


		 // How long did the pipeline take?
		//std::cout << std::endl << "Pipeline Time: " << (std::clock() - program_start) / (double)(CLOCKS_PER_SEC /1000) << " ms " << std::endl << std::endl << std::flush;		   
		//frameCount++;

	}
    }
	
    catch (const std::exception& e)
    {
	std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}

