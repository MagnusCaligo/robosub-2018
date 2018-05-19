#include "computerVisionComm.hpp"
#include <map>
#include <string>
#include <stdio.h>
#include <iostream>


ComputerVisionComm::ComputerVisionComm()
{
}

// return: visionParams
GuiParameters ComputerVisionComm::getGuiParameters()
{
    return guiParameters;
}

/*************
 * use
 * 	- To recieve a message from the python client side and
 * 	  parse the input to be read.
 *
 * parameters
 * 	- context -> context from main 
 * 	- socket  -> socket from main
 ************/
GuiParameters ComputerVisionComm::getMessage(zmq::context_t &context, zmq::socket_t &socket)
{
    zmq::message_t request;
    socket.recv(&request);
    std::string replyMessage = std::string(static_cast<char *>(request.data()), request.size());

    Json::Value root;
    Json::Reader reader;
    bool parsingSuccessful = reader.parse(replyMessage, root);

    // IF THERE IS A ERROR: STOI THAT IS BECAUSE THE VALUES WE ARE LOOKING
    // FOR IS RETURNING NULL WHICH MEANS THAT THE VALUES DONT MATCH THE GUI
    std::string hueMax = root.get("hueMax", "UTF-8").asString(); // 1
    std::string hueMin = root.get("hueMin", "UTF-8").asString(); // 2
    std::string saturationMin = root.get("saturationMin", "UTF-8").asString(); // 3
    std::string saturationMax = root.get("saturationMax", "UTF-8").asString(); // 4
    std::string valueMin = root.get("valueMin", "UTF-8").asString(); // 5
    std::string valueMax = root.get("valueMax", "UTF-8").asString(); // 6
    std::string min_disparity = root.get("min_disparity", "UTF-8").asString(); // 7
    std::string max_disparity = root.get("max_disparity", "UTF-8").asString(); // 8
    std::string P1 = root.get("P1", "UTF-8").asString(); // 9
    std::string P2 = root.get("P2", "UTF-8").asString(); // 10
    std::string sad = root.get("sad", "UTF-8").asString(); // 11
    std::string bt_clip_value = root.get("bt_clip_value", "UTF-8").asString(); // 12
    std::string max_diff = root.get("max_diff", "UTF-8").asString(); // 13
    std::string uniqueness_ratio = root.get("uniqueness_ratio", "UTF-8").asString(); // 14
    std::string scanlines_mask = root.get("scanlines_mask", "UTF-8").asString(); // 15
    std::string ct_win_size = root.get("ct_win_size", "UTF-8").asString(); // 16
    std::string hc_win_size = root.get("hc_win_size", "UTF-8").asString(); // 17
    std::string cannyMin = root.get("cannyMin", "UTF-8").asString(); // 18
    std::string cannyMax = root.get("cannyMax", "UTF-8").asString(); // 19
    std::string confidenceThreshold = root.get("confidenceThreshold", "UTF-8").asString(); // 20

    std::string useNN = root.get("useNN", "UTF-8").asString(); // 1
    std::string useImage = root.get("useImage", "UTF-8").asString(); // 2 
    std::string useVideo = root.get("useVideo", "UTF-8").asString(); // 3 
    std::string cameraCheck = root.get("cameraCheck", "UTF-8").asString(); // 4
    std::string useCameras = root.get("useCameras", "UTF-8").asString(); // 5

    std::string currentMission = root.get("currentMission", "UTF-8").asString(); // 1 
    std::string obstacleNames = root.get("obstacleNames", "UTF-8").asString(); // 2 
    std::string nnPath = root.get("nnPath", "UTF-8").asString(); // 3 
    std::string imagePath = root.get("imagePath", "UTF-8").asString(); // 4 
    std::string videoPath = root.get("videoPath", "UTF-8").asString(); // 5 
	std::string frameSkip = root.get("frameSkip", "15").asString();

    GuiParameters guiParameters;
    guiParameters.insert(std::make_pair("hueMax", hueMax));
    guiParameters.insert(std::make_pair("hueMin", hueMin));
    guiParameters.insert(std::make_pair("saturationMax", saturationMax));
    guiParameters.insert(std::make_pair("saturationMin", saturationMin));
    guiParameters.insert(std::make_pair("valueMax", valueMax));
    guiParameters.insert(std::make_pair("valueMin", valueMin));
    guiParameters.insert(std::make_pair("min_disparity", min_disparity));
    guiParameters.insert(std::make_pair("max_disparity", max_disparity));
    guiParameters.insert(std::make_pair("P1", P1));
    guiParameters.insert(std::make_pair("P2", P2));
    guiParameters.insert(std::make_pair("sad", sad));
    guiParameters.insert(std::make_pair("bt_clip_value", bt_clip_value));
    guiParameters.insert(std::make_pair("max_diff", max_diff));
    guiParameters.insert(std::make_pair("uniqueness_ratio", uniqueness_ratio));
    guiParameters.insert(std::make_pair("scanlines_mask", scanlines_mask));
    guiParameters.insert(std::make_pair("ct_win_size", ct_win_size));
    guiParameters.insert(std::make_pair("hc_win_size", hc_win_size));
    guiParameters.insert(std::make_pair("cannyMin", cannyMin));
    guiParameters.insert(std::make_pair("cannyMax", cannyMax));
    guiParameters.insert(std::make_pair("confidenceThreshold", confidenceThreshold));
    guiParameters.insert(std::make_pair("useNN", useNN));
    guiParameters.insert(std::make_pair("useImage", useImage));
    guiParameters.insert(std::make_pair("useVideo", useVideo));
    guiParameters.insert(std::make_pair("cameraCheck", cameraCheck));
    guiParameters.insert(std::make_pair("useCameras", useCameras));
    guiParameters.insert(std::make_pair("currentMission", currentMission));
    guiParameters.insert(std::make_pair("obstacleNames", obstacleNames));
    guiParameters.insert(std::make_pair("nnPath", nnPath));
    guiParameters.insert(std::make_pair("imagePath", imagePath));
    guiParameters.insert(std::make_pair("videoPath", videoPath));
	guiParameters.insert(std::make_pair("frameSkip", frameSkip));

    return guiParameters;
}

/*************
 * use
 * 	- Sends the class variable responseMessage to the python side
 * parameters
 * 	- context -> context from main
 * 	- socket  -> socket from main
 ************/
void ComputerVisionComm::sendResponse(zmq::context_t &context, zmq::socket_t &socket, std::string msgToClient)
{
    zmq::message_t reply(msgToClient.size());
    memcpy((void *) reply.data(), (msgToClient.c_str()), msgToClient.size());
    socket.send(reply);

}

/*
 * use
 *     - Prases the message then converts the message to the
 *       GuiParameters map.
 * parameters
 *     - Reponse message from client
 */
void ComputerVisionComm::parseMessage(std::string &replyMessage)
{
}
