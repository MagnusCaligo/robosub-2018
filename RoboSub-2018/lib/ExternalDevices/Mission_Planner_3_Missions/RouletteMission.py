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

	'''
	USE_BOTTOMCAM = self.useBottomCamera; 
	USE_FRONTCAM = self.useFrontCamera;
	'''
	self.calculatedWaypoint = None
	

#       ********Roulette Detections********           
	self.FrontCam_RouletteFound = False
	self.BottomCam_RouletteFound= False
	self.ROULETTEBOARD = None
	
#	********Roulette MiddlePosition****

	self.Roulette_ClassNumber = 7
	self.src_pts = [(0,0,0),(0,990.6,0),(990.6,990.6,0),(0,0,990.6)]
	self.img_pts = None

	#Location of Roulette board
	self.Roulette_Waypoint= None

#	Fake Camera Matrix
	self.cameraMatrix = [[808,     0, 404],
			     [   0, 608 , 304],
			     [   0,    0, 1.0],]


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


    def Orient_Above_Board(self):
	TOP_LEFT_CORNER = (self.ROULETTEBOARD[1] - 990.6/2, self.ROULETTEBOARD[2]- 990.6/2)
	TOP_RIGHT_CORNER = (self.ROULETTEBOARD[1] + 990.6/2,self.ROULETTEBOARD[2] - 990.6/2)
	BOTTOM_LEFT_CORNER = (self.ROULETTEBOARD[1] - 990.6/2 , self.ROULETTEBOARD[2] + 990.6/2 )
	BOTTOM_RIGHT_CORNER = (self.ROULETTEBOARD[1] + 990.6/2 ,self.ROULETTEBOARD[2] + 990.6/2 )
	self.img_pts = [TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER];
	self.writeDebugMessage("Lining up with Board...")
	rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(self.img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
	p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, tvec[0], -tvec[2], -tvec[1], 0, 0, 0)
	self.Roulette_Waypoint = [n,e,u,y,p,r]
	self.moveToWaypoint(self.Roulette_Waypoint)
	
	
#-----------------------END------------------------#
    def UPDATE_VIZUALS(self):
#	FRONT CAMERA VIZUALS
	self.useFrontCamera()#  see top for function
	self.FrontCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.ROULETTEBOARD = det;
			self.FrontCam_RouletteFound = True
	
#	BOTTOM CAMERA VIZUALS
	self.useBottomCamera()#  see top for function

	self.BottomCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.ROULETTEBOARD = det;
			self.BottomCam_RouletteFound = True


#-----The UPDATE: Essentially the main-------#

    def update(self):

	
	self.UPDATE_VIZUALS();
	self.writeDebugMessage("Vizuals updated...Beginning logic\n")
	if( self.FrontCam_RouletteFound or self.BottomCam_RouletteFound ):
	    if( self.BottomCam_RouletteFound ):
		self.Orient_Above_Board();
	    else:
		self.Move_Above_Board();

	else:
	    self.writeDebugMessage("Target not found...spinning")
	    self.Search_RouletteBoard()




