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

# ------------EXPERIMENT-------------- #

	self.NUMPY_ARRAY = np.arange(10);

# ---------END EXPERIMENT------------- #



#	Camera Type to Use

	'''
	USE_BOTTOMCAM = self.useBottomCamera; 
	USE_FRONTCAM = self.useFrontCamera;
	'''
	self.calculatedWaypoint = None
	self.ACTIVE_CAM = "None";
	self.COUNT_FRONT = 0;
	self.COUNT_BACK  = 0;
	self.NUMBER_OF_SAMPLES = 175;
	self.CALCULATED_WAYPOINT = None;	

#       ********Roulette Detections*********          
	self.FrontCam_RouletteFound  = False;
	self.BottomCam_RouletteFound = False;
#	************************************


	self.ROULETTEBOARD = [];
	self.SOLVED_BOARD = [];
	self.BOARDSOLVED_FRONT = False;
	self.BOARDSOLVED_BACK  = False; 
	self.END_FIRST = None;

	self.NE_COMPONENT = None
	
#	********Roulette MiddlePosition****

	self.Roulette_ClassNumber = 7;
	self.src_pts = [(0,0,0),(0,3.25,0),(3.25,3.25,0),(3.25,0,0)]
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
#-------------------------END-------------------------#
    def EUCLIDIAN_MEDIAN(self,GUESS, Comparison_Array):
	Comparison_Array.pop(0);
	dy_new = GUESS;
	y_old = (10,10); #some Random Values
	tol = .005
	L1 = [];
	L2 = [];
	while( tol < abs(y_new[0] - y_old[0]) and tol < abs(y_new[1] - y_old[1]) ):
		for x in Comparison_Array:
			x_y = (x[0] - y_new[0], x[1] - y_new[1]);

			print("THIS IS THE VECTOR: "+str(x_y))
			
			NORM = math.sqrt(x_y[0]**2 + x_y[1]**2);
			
			print("THIS IS THE NORM: "+str(NORM))
			if(NORM == 0):
				NORM = 1;
			
			L1.append( (x[0]/NORM, x[1]/NORM) )
			L2.append( 1/NORM )

		TOP    = [ sum(x) for x in zip(*L1) ]
		print(TOP)
		BOTTOM = sum(L2)
		y_old  = y_new;
		y_new  = (TOP[0]/BOTTOM,TOP[1]/BOTTOM)
		L1 = [];
		L2 = [];
	return y_new[0],y_new[1],y_new[2]

#-----------------------END------------------------#

    def SOLVING_PNP(self):
	SOLVED_BOARD = [];
	for BRD in self.ROULETTEBOARD:
		TOP_LEFT_CORNER = (BRD[1] - BRD[3]/2, BRD[2]- BRD[4]/2)
		TOP_RIGHT_CORNER = (BRD[1] + BRD[3]/2/2,BRD[2] - BRD[4]/2/2)
		BOTTOM_LEFT_CORNER = (BRD[1] - BRD[3]/2/2 , BRD[2] + BRD[4]/2/2 )
		BOTTOM_RIGHT_CORNER = (BRD[1] + BRD[3]/2/2 ,BRD[2] + BRD[4]/2/2 )
		self.img_pts = [TOP_LEFT_CORNER, BOTTOM_LEFT_CORNER, BOTTOM_RIGHT_CORNER, TOP_RIGHT_CORNER];


		rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(self.img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
		print("TVEC:"+str(tvec))
		

		po, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, tvec[0][0], 0, -tvec[2][0], 0, 0, 0)
		print("DISTANCE:"+str(math.sqrt(e**2 + n**2)))

		self.SOLVED_BOARD.append([n,e,self.finalWaypoint[2],self.calculatedWaypoint[3],0,0]); #MAKES a vector where the last index can be compared

#-----------------------END------------------------#
		
#    def FREQUENCY_UPDATE(self):
#	for BRD in SOLVED_BOARD:

#-----------------------END------------------------#
    def LINED_UP_WITH_CENTER(self,det):
	if(  808*2/5 < det[1] and det[1] < 808*3/5 and 608*2/5 < det[2] and det[2] < 608*3/5):
		pass;
		print("Done...");
		return True;
	else:
		print("Lining up pitch and yaw...")
		if( det[1] < 808*2/5  ):
			self.moveToWaypoint([self.position[0], self.position[1], self.position[2], self.orientation[0] - .5, self.orientation[1], self.orientation[2]]);

		else:
			self.moveToWaypoint([self.position[0], self.position[1], self.position[2], self.orientation[0] + .5, self.orientation[1], self.orientation[2]]);
		if( det[2] < 608*2/5  ):
			self.moveToWaypoint([self.position[0], self.position[1], self.position[2], self.orientation[0], self.orientation[1] + .2, self.orientation[2]]);
		else:
			self.moveToWaypoint([self.position[0], self.position[1], self.position[2], self.orientation[0], self.orientation[1] - .2, self.orientation[2]]);

		return False;

#-----------------------END------------------------#
    def UPDATE_VIZUALS(self):

	self.useFrontCamera()#  see top for function

	if( self.BOARDSOLVED_FRONT == False):

		for det in self.detectionData:
			if det[0] == self.Roulette_ClassNumber:
				if(self.COUNT_FRONT < self.NUMBER_OF_SAMPLES and self.LINED_UP_WITH_CENTER(det)):
					self.COUNT_FRONT += 1;
					self.ROULETTEBOARD.append(det);
					self.FrontCam_RouletteFound = True
					return -1;

#------------------------------------------------------------------------------#	
#	if( self.BOARDSOLVED_FRONT == True ):	
#		self.useBottomCamera()#  see top for function
#		#self.BottomCam_RouletteFound = False
#		for det in self.detectionData:
#			if det[0] == self.Roulette_ClassNumber:
#				self.COUNT_BACK += 1;
#				self.BottomCam_RouletteFound = True
#				self.ROULETTEBOARD.append(det);	
#------------------------------------------------------------------------------#



#	self.useBottomCamera()#  see top for function

#	self.BottomCam_RouletteFound = False
	#for det in self.detectionData:
	#	if det[0] == self.Roulette_ClassNumber:
	#		self.BottomCam_RouletteFound = True
	#		self.ROULETTEBOARD.append(det);
			
#---------SPECIAL KEY FOR SORTIING----------#
    def CHOOSE_SECOND_ELEMENT(self,elm):
		return elm[-1];

#-----The UPDATE: Essentially the main-------#

    def update(self):
	print("-------------------------------------NEW RUN--------------------------------------------------------")

		
	self.UPDATE_VIZUALS(); #ALWAYS RUNNING


	if( self.FrontCam_RouletteFound or self.BottomCam_RouletteFound ): # HAS BEEN SEEN ONCE
		if( self.COUNT_FRONT < self.NUMBER_OF_SAMPLES and self.FrontCam_RouletteFound == True): #Case for Top
			self.moveToWaypoint(self.calculatedWaypoint);
			print("...Collecting Data for Front");
			print("COUNT:"+str(self.COUNT_FRONT))

		elif( self.COUNT_BACK < self.NUMBER_OF_SAMPLES and self.BottomCam_RouletteFound == True):#Case for Bottom
			self.moveToWaypoint(self.calculatedWaypoint);
			print("...Collecting Data for Bottom");
			print("COUNT:"+str(self.COUNT_BACK))
		else:
		
			if(self.BOARDSOLVED_FRONT == False):# and self.BOARDSOLVED_BACK == False):

				self.SOLVING_PNP()
				self.SOLVED_BOARD.sort(key=self.CHOOSE_SECOND_ELEMENT);

				self.NE_COMPONENT = self.EUCLIDIAN_MEDIAN( (10,10) , [(Components[0],Components[1]) for Components in self.SOLVED_BOARD] )

				self.ROULETTEBOARD = [];
				self.BOARDSOLVED_FRONT = True

		#--------------------------------------------------------------------------------------------------------#
		#	elif( self.BOARDSOLVED_BACK == False ):
		#		self.SET_IN_CENTER();
		#		self.SOLVING_PNP()
		#		self.SOLVED_BOARD.sort(key=self.CHOOSE_SECOND_ELEMENT);
		#		self.FREQUENCY_UPDATE();
		#		self.BOARDSOLVED_BACK = True;
		#
		#	if(self.BOARDSOLVED_FRONT == True):
		#		self.END_FIRST = False; 
		#--------------------------------------------------------------------------------------------------------#

			self.movetToWaypoint(self.NE_COMPONENT[0], self.NE_COMPONENT[1], self.finalWaypoint[2], self.calculatedWaypoint[3],0,0)
			print("...Moving to Waypoint" + str([self.NE_COMPONENT[0], self.NE_COMPONENT[1], self.position[2], self.calculatedWaypoint[3],0,0]))

	else:
		self.Search_RouletteBoard()

	print("------------------------------------END RUN---------------------------------------------------------\n\n")
	


