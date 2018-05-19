#ifndef __COMPUTERVISIONCOMM_HPP__
#define __COMPUTERVISIONCOMM_HPP__

#include <zmq.hpp>
#include <map>
#include <vector>
#include <iostream>
#include <memory>
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <string>
#include <json/json.h>
#include <json/reader.h>
#include <json/value.h>

// Map of obstacle attributes:
// "Detection" : [label, probability, cx, cy, width, height]
// "Distance" : [how far the object is ]
// "Pose" : [yaw, pitch, roll]
typedef std::map<std::string, std::vector<float>> Obstacle;
typedef std::map<std::string, std::string> GuiParameters;
typedef std::vector<float> Detection;
typedef std::vector<float> Distance;
typedef std::vector<float> Pose;

class ComputerVisionComm
{
public:
    ComputerVisionComm();

    GuiParameters getGuiParameters();
    GuiParameters getMessage(zmq::context_t &, zmq::socket_t &);
    void parseMessage(std::string &);
    void sendResponse(zmq::context_t &, zmq::socket_t &, std::string );

    int hueMax, hueMin, saturationMin, saturationMax, valueMax, valueMin,
	min_disparity, max_disparity, P1, P2, sad, bt_clip_value, max_diff,
	uniqueness_ratio, scanlines_mask, ct_win_size, hc_win_size, cannyMin,
	cannyMax, confidenceThreshold;

    std::string useNN, useImage, useVideo, cameraCheck, useCameras;

    std::string currentMission, obstacleNames, nnPath, imagePath, videoPath;


private:
    std::map<std::string, std::string> guiParameters;
    std::vector<Obstacle> obstacles;
};


#endif
