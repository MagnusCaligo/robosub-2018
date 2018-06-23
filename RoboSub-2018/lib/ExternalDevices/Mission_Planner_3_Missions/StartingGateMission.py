from abstractMission import AbstractMission
import cv2
import time
import numpy as np

 
class StartingGateMission(AbstractMission):
    
    defaultParameters = AbstractMission.defaultParameters + "Gate_Side = Left\n" + "Gate_Color = Red\n"#"Test = False\n" + "sColor = UNSPEC"; # Add Any Necessary Parameters

    def __init__(self, parameters): #Waypoint Handling of events
        AbstractMission.__init__(self, parameters)


    def initalizeOnMissionStart(self):
	AbstractMission.initalizeOnMissionStart(self)

        self.Waypoint_Reached = False #Way of telling if we are within error of the waypoint
        self.atWaypointStartTime = None #Sets the start time from the moment we are at the waypoint so we can stay there for as long as we need to

        #---Relevant Gate Info---#
        self.Gate_In_Sight = False;
        self.Gate_Side = "Left";
        self.Gate_Color= "Red";
        self.Arms_In_Sight = False;
        self.UNORDERED_GATE_COMPONENTS = ["EMPTY","EMPTY","EMPTY"];

        self.src_pts = [(0,0,0),(.25,0,0),(.25,3.5,0),(0,3.5,0)]
        
        #--Variables--#
        self.calculatedWaypoint = None

        self.leftArmPosEst = None
        self.rightArmPosEst = None
        self.topPosEst = None
        
        self.leftArmPosSum = []
        self.rightArmPosSum = []
	self.movementDestination = None
        
        self.armClassNumber = 15
        self.topClassNumber = 16

        
        
        #--Timing Stuff--#
        self.rotateTimer = None
        self.rotateWaitTime = 5

        self.Left_Side = None#
        self.Right_Side = None#
#----------------------END----------------------------#
    """ Takes unKnown Arms and Sorts them then returns them as 'Left' 'Right' """
    def Determine_Left_From_Right(Arm1, Arm2):
        if(Arm1 > Arm2):
            return Arm2, Arm1;
        else:
            return Arm1, Arm2;

    def Error_Redux(self):
	if(self.Left[2] > 40):
		posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position, self.Left - 5 ,0,0, 45, 0,0);
		Error = [posedata, n,e,u, pitch, yaw, roll];
		self.moveToWaypoint(Error)
	if(self.Right[2] < 768)
		posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position, self.Right + 5 ,0,0, 45, 0,0);
		Error = [posedata, n,e,u, pitch, yaw, roll];
		self.moveToWaypoint(Error)
	else:
		print("READY AND COMPLETE"):
		return 1;
	

#----------------------END----------------------------#
    def Gate_Vizualization(self):
        __gate = []; """Basic List to contain updated components"""
        Arm_Count = 0;
        Part_Count = 0;
        for Object in self.detectionData:

            if( Object[0] == self.armClassNumber):
                    
                __gate.append(Object);
                Arm_Count  +=1;
                Part_Count +=1;

            if( Object[0] == self.topClassNumber):
                __gate.append(Object);
                Part_Count +=1;

            if( Arm_Count > 1 ):

                self.Gate_In_Sight = True;

            else:

                self.Gate_In_Sight = False;

        if( not self.Gate_In_Sight):
            self.UNORDERED_GATE_COMPONENTS = ["EMPTY","EMPTY","EMPTY"];

        #---Means Of Sorting Left from Right----#
        if(self.Arms_In_Sight):

            if(  __gate[0][2] == self.topClassNumber):
                self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[1][2],__gate[2][2]);
            elif(__gate[1][2] == self.topClassNumber):
                self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[0][2],__gate[2][2]);
            else:
                self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[0][2],__gate[1][2]);

        self.UNORDERED_GATE_COMPONENTS = __gate;

    #----------------------MISSION LOGIC I----------------------------#


    def Christians_Method(self, Gate_Side):
        if(self.Arms_In_Sight):
	#------If In Defined Pixel Range------#
		'''	
		if(self.Left_Side[2] < 40 and self.Left_Side[3] > -40 ):
			#Strafe_Right();
		elif(self.Right_Side[2] >768 and self.Right_Side[3] < -568):
			#Strafe_Left();
		elif(self.Left_Side[2] < 40 and self.Left_Side[3] > -40 and self.Right_Side[2] >768 and self.Right_Side[3] < -568):

		else:
		'''

		Error_Redux();	


        else:
        	print("Arms not in sight...")
		return -1;
            #Straif Left Around Fixed Point
            #1) Update YAW 
            #2) relativeMoveXYZ
    #----------------------MISSION LOGIC II----------------------------#        
    def algorithm2(self):
        detections = []
        for detection in self.detectionData:
            if detection[0] == self.armClassNumber:
                detections.append(detection)
        

        if len(detections) >1: # We can see both arms
	    print "We saw an arm!"
            leftArmDetection = None
            rightArmDetection = None
            if detections[0][1] <= detections[1][1]: #Determine which side is left and right based on location in image
                leftArmDetection = detections[0]
                rightArmDetection = detections[1]
            else:
                leftArmDetection = detections[1]
                rightArmDetection = detections[0]
                
            if leftArmDetection[2] + leftArmDetection[4] < 608 - 30 and leftArmDetection[3] > 30: #We need to check that we can see the entire post; if not then we can't use solvePnP
                img_pts = [(leftArmDetection[1], leftArmDetection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
                rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
                tvec[0][0]-=.25 #Camera isn't centered with Percy, so move it over a bit
                tvec[1][0]+=2.5 #tvec is from top left corner, so we want to move a bit deeper
                tvec[2][0] *= -1 #Z decreases towards the front of the sub, so if we want to move forward this needs to be negative
                self.leftArmPosSum.append(tvec)
                nAvg = 0
                eAvg = 0
                uAvg = 0
                for values in self.leftArmPosSum:
                    nAvg += values[0]
                    eAvg += values[1]
                    uAvg += values[2]
                nAvg /= len(self.leftArmPosSum)
                eAvg /= len(self.leftArmPosSum)
                uAvg /= len(self.leftArmPosSum)
                self.leftArmPosEst = [nAvg, eAvg, uAvg]

            if rightArmDetection[2] + rightArmDetection[4] < 608 - 30 and rightArmDetection[2] > 30: #We need to check that we can see the entire post; if not then we can't use solvePnP
                img_pts = [(rightArmDetection[1], rightArmDetection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
                rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
                tvec[0][0]-=.25 #Camera isn't centered with Percy, so move it over a bit
                tvec[1][0]+=2.5 #tvec is from top left corner, so we want to move a bit deeper
                tvec[2][0] *= -1 #Z decreases towards the front of the sub, so if we want to move forward this needs to be negative
                self.rightArmPosSum.append(tvec)
                nAvg = 0
                eAvg = 0
                uAvg = 0
                for values in self.rightArmPosSum:
                    nAvg += values[0]
                    eAvg += values[1]
                    uAvg += values[2]
                nAvg /= len(self.rightArmPosSum)
                eAvg /= len(self.rightArmPosSum)
                uAvg /= len(self.rightArmPosSum)
                self.rightArmPosEst = [nAvg, eAvg, uAvg]

            
            self.movementDestination = []
            if self.parameters["Gate_Side"] in ["Left", "left", "l"]:
                self.movementDestination = self.leftArmPosEst
            else:
                self.movementDestination = self.rightArmPosEst
            self.movementDestination[3] = self.finalWaypoint[3]
            self.movementDestination[4] = 0
            self.movementDestination[5] = 0 
            return self.moveToWaypoint(self.movementDestination)
        elif len(detections) == 1: #We only see one arm, so move towards it
	    if self.movementDestination == None:
		    detection = detections[0]
		    img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
		    rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
		    tvec[0][0]-=.25 #Camera isn't centered with Percy, so move it over a bit
		    tvec[1][0]+=2.5 #tvec is from top left corner, so we want to move a bit deeper
		    tvec[2][0] *= -1 #Z decreases towards the front of the sub, so if we want to move forward this needs to be negative
		    rotationDifference = math.degrees(math.atan2(tvec[0], tvec[2]))
		    pose, n, e, u, p, y, r = self.movementController.relativeMoveXYZ(self.orientation + self.position, tvec[0][0], tvec[1][0], tvec[2][0], 0, rotationDifference, 0)
		    waypoint = [n,e,u, self.finalWaypoint[3], 0, 0]
		    self.moveToWaypoint(waypoint)
	    else:
		    return self.moveToWaypoint(self.movementDestination)

		
    #----------------------MAIN_FUNCTION------------------#

    def update(self):
	
        #---Vizualization Questions---#

        self.Gate_Vizualization();
	
	self.Gate_In_Site = False
	for det in self.detectionData:
		if det[0] == self.armClassNumber:# or det[0] == self.topClassNumber:
			self.Gate_In_Sight = True
			print "We see the gate"
		

        #----Move to Waypoint----#
        if(not self.Waypoint_Reached and not self.Gate_In_Sight):
	    print "Moving to waypoint"
            self.Waypoint_Reached = self.moveToWaypoint(self.finalWaypoint);

        #----Check for Visual, or Waypoint Reached-----#
        if(self.Waypoint_Reached or self.Gate_In_Sight):
            self.Waypoint_Reached = True;

        if( (self.Gate_In_Sight is False) and (self.Waypoint_Reached is True) ):
            #REORIENT (*spin*)
            if self.rotateTimer == None:
                self.rotateTimer = time.time()
            if time.time() - self.rotateTimer >= self.rotateWaitTime:
                self.rotateTimer = None
                self.calculatedWaypoint = None
            if self.calculatedWaypoint == None:
                posedata, n,e,u, pitch, yaw, roll = self.movementController.relativeMoveXYZ(self.orientation + self.position,0,self.position[2] - self.finalWaypoint[2],0, 45, 0,0);
                self.calculatedWaypoint = [n,e,u,yaw,pitch,roll]
            self.moveToWaypoint(self.calculatedWaypoint);

        if( (self.Gate_In_Sight is True) and (self.Waypoint_Reached is True) ):
            print "beginning algorithm"
            #METHOD INPUT-----START:
            #self.Christians_Method(Gate_Side); """Who needs naming conventions anyway..."""
            self.algorithm2()
            #METHOD INPUT-----END:

#----------------------END----------------------------#		
		





"""---------------------------------------------------
	    if(isGate() == True):
		if(observed_color == desired_color):

		    Direct_Move_Foreward(); #Move through Gate
		    printf("\nMission Complete...");
		    self.writeDebugMessage("Mission Complete");
		else:

		    Reorient(observed_color); #correct Position
	    else:
		printf("Moving\n")
		self.writeDebugMessage("Moving...\n")

        -----------------------------------------------

	atWaypoint = self.moveToWaypoint(self.finalWaypoint)
        if atWaypoint:
            if self.sentMessage1 == False:
                self.writeDebugMessage("At Waypoint")
                self.sentMessage1 = True
            self.atWaypoint = True
        else:
            self.atWaypoint = False
            self.sentMessage1 = False
            self.atWaypointStartTime = None

        if self.atWaypoint == True:
            if self.atWaypointStartTime == None:
                self.atWaypointStartTime = time.time()
            if time.time() - self.atWaypointStartTime >= int(self.parameters["waitTime"]):
                self.writeDebugMessage("Finished The Waypoint")
                return 1 #Signal the mission is over
        else:
            self.atWaypointStartTime = None

	--------------------------------------------------"""
