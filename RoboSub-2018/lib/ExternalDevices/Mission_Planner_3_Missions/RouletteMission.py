from abstractMission import AbstractMission
import cv2
import numpy as np
import math
import time

#TODO When it sees the Roulette board, immidiately use its location to determine where we need to go, do not constantly update

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
	self.ACTIVE_CAM = "None";
	self.COUNTING =0;
	

#       ********Roulette Detections********           
	self.FrontCam_RouletteFound = False
	self.BottomCam_RouletteFound= False;
	self.ROULETTEBOARD = [];
	self.SOLVED_BOARD = [];
	self.BOARDSOLVED = False;
	
#	********Roulette MiddlePosition****

	self.Roulette_ClassNumber = 2;
	self.src_pts = [(0,0,0),(0,3.25,0),(3.25,3.25,0),(0,0,3.25)]
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
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,2,0, 45, 20,0);#Overwritten Y axis
		self.calculatedWaypoint = [self.finalWaypoint[0],self.finalWaypoint[1],self.finalWaypoint[2],yaw,self.generalWaypoint[4],0]#REMOVED PITCH AND ROLL
	print("FOUND:"+str(self.FrontCam_RouletteFound));
	self.moveToWaypoint(self.calculatedWaypoint);

#-----------------------END------------------------#


    def Move_Above_Board(self):
	
	self.useFrontCamera()

	print("Moving Forward...")
	p, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, 0, 2, -1, 0, 0, 0)
	self.Roulette_Waypoint = [n,e,self.finalWaypoint[2],y,0,0]
	self.moveToWaypoint(self.Roulette_Waypoint)

    def SOLVING_PNP(self):
	for BRD in self.ROULETTEBOARD:
		TOP_LEFT_CORNER = (BRD[1] - BRD[3]/2, BRD[2]- BRD[4]/2)
		TOP_RIGHT_CORNER = (BRD[1] + BRD[3]/2/2,BRD[2] - BRD[4]/2/2)
		BOTTOM_LEFT_CORNER = (BRD[1] - BRD[3]/2/2 , BRD[2] + BRD[4]/2/2 )
		BOTTOM_RIGHT_CORNER = (BRD[1] + BRD[3]/2/2 ,BRD[2] + BRD[4]/2/2 )
		self.img_pts = [TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER];

		rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(self.img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
		po, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, -tvec[0][0]/2, -tvec[2][0]/2, -tvec[1][0]/2, 0, 0, 0)
		self.SOLVED_BOARD.append([n,e,u,y,p,r,math.sqrt( e**2 + n**2 )]); #MAKES a vector where the last index can be compared
	
	
#-----------------------END------------------------#
    def UPDATE_VIZUALS(self):
#	FRONT CAMERA VIZUALS
	#if(self.ACTIVE_CAM != "Front"):
	self.useFrontCamera()#  see top for function
	#	self.ACTIVE_CAM = "Front";
#	self.FrontCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.ROULETTEBOARD.append(det);
			self.FrontCam_RouletteFound = True
	
#	BOTTOM CAMERA VIZUALS
	self.useBottomCamera()#  see top for function

#	self.BottomCam_RouletteFound = False
	for det in self.detectionData:
		if det[0] == self.Roulette_ClassNumber:
			self.BottomCam_RouletteFound = True
			self.ROULETTEBOARD.append(det);
			
#---------SPECIAL KEY FOR SORTIING----------#
    def CHOOSE_SECOND_ELEMENT(self,elm):
		return elm[6];

#-----The UPDATE: Essentially the main-------#

    def update(self):
	print("-------------------------------------NEW RUN--------------------------------------------------------")

		
	self.UPDATE_VIZUALS();

	if( self.FrontCam_RouletteFound or self.BottomCam_RouletteFound ):
		print("...Holding Position");
		if(self.COUNTING <= 30):
			self.COUNTING += 1;
			self.moveToWaypoint(self.calculatedWaypoint);
		elif(self.COUNTING > 30 and self.BOARDSOLVED == False):
			self.SOLVING_PNP()
			self.BOARDSOLVED = False;
			self.SOLVED_BOARD.sort(key=self.CHOOSE_SECOND_ELEMENT);
		else:
			self.moveToWaypoint(self.SOLVED_BOARD[15][:-1])
	else:
		self.Search_RouletteBoard()

	print("------------------------------------END RUN---------------------------------------------------------\n\n")
'''
	print("-------------------------------------NEW RUN--------------------------------------------------------")
	self.UPDATE_VIZUALS();
	print("Vizuals updated...Beginning logic\n")
	if( self.FrontCam_RouletteFound or self.BottomCam_RouletteFound ):
	    if( self.BottomCam_RouletteFound ):
		self.Orient_Above_Board();
	    else:
		self.Move_Above_Board();

	else:
	    print("Target not found...spinning")
	    self.Search_RouletteBoard()
	print("------------------------------------END RUN---------------------------------------------------------\n\n")
'''
	




