from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

class RouletteMission(AbstractMission):

    defaultParameters = AbstractMission.defaultParameters + "Bottom_Camera_Exists_In_Code = False\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

#----Things_That_Need_Initialization_----#
    def initalizeOnMissionStart(self):
	AbstractMission.initalizeOnMissionStart(self)

#	Camera Type to Use

	USE_BOTTOMCAM = self.useBottomCamera; 
	USE_FRONTCAM = self.useFrontCamera;

	self.calculatedWaypoint = None
	

#       ********Roulette Detections********           
	self.FrontCam_RouletteFound = False
	self.BottomCam_RouletteFound= False

	#TODO Change this number to actual value
	self.Roulette_ClassNumber = None

	#Location of Roulette board
	self.Roulette_Waypoint= None


	#--Timing Stuff--#
        self.rotateTimer = None
        self.rotateWaitTime = 5

#-------------------------END-------------------------#

    def Search_RouletteBoard(self):
	#Spinning until Found
	if self.rotateTimer == None:
		self.rotateTimer = time.time()
	if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
        if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.position[2] - self.finalWaypoint[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,u,yaw,pitch,roll]
        self.moveToWaypoint(self.calculatedWaypoint);

#-----------------------END------------------------#


    def Move_Above_Board(self):
	self.writeDebugMessage("Moving Forward...")
	p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0, 0, -1, 0, 0, 0)
	self.Roulette_Waypoint = [n,e,u,y,p,r]
	self.moveToWaypoint(self.Roulette_Waypoint)


#TODO    def Orient_Above_Board(self):
	
#-----------------------END------------------------#
    def UPDATE_VIZUALS(self):
#	FRONT CAMERA VIZUALS
	USE_FRONTCAM # see top for function
	self.FrontCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.FrontCam_RouletteFound = True
	
#	BOTTOM CAMERA VIZUALS
	USE_BOTTOMCAM; # see top for function

	self.BottomCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.BottomCam_RouletteFound = True


#-----The UPDATE: Essentially the main-------#

    def update(self):


	self.UPDATE_VIZUALS();

	if( self.FrontCam_RouletteFound or self.BottomCam_RouletteFound ):
	    if( self.BottomCam_RouletteFound ):
		self.Orient_Above_Board();
	    else:
		self.writeDebugMessage("Will Spin Above Target...")
		self.Move_Above_Board();

	else:
	    self.Search_RouletteBoard()




