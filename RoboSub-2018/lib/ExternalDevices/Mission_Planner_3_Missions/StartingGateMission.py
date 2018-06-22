from abstractMission import AbstractMission
import time


class StartingGateMission(AbstractMission):
    
    defaultParameters = AbstractMission.defaultParameters + "Gate_Side = Left\n" + "Gate_Color = Red\n"#"Test = False\n" + "sColor = UNSPEC"; # Add Any Necessary Parameters

    def __init__(self, parameters): #Waypoint Handling of events
        AbstractMission.__init__(self, parameters)

        self.Waypoint_Reached = False #Way of telling if we are within error of the waypoint
        self.atWaypointStartTime = None #Sets the start time from the moment we are at the waypoint so we can stay there for as long as we need to

	#---Relevant Gate Info---#
	self.Gate_In_Sight = False;
	self.Gate_Side = "Left";
	self.Gate_Color= "Red";
	self.Arms_In_Sight = False;
	self.UNORDERED_GATE_COMPONENTS = ["EMPTY","EMPTY","EMPTY"];


	self.Left_Side = #
	self.Right_Side = #
#----------------------END----------------------------#
""" Takes unKnown Arms and Sorts them then returns them as 'Left' 'Right' """
    def Determine_Left_From_Right(Arm1, Arm2):
	if(Arm1[3] > Arm2[3]):
		return Arm2, Arm1;
	else:
		return Arm1, Arm2;

#----------------------END----------------------------#
    def Gate_Vizualization():
	__gate = []; """Basic List to contain updated components"""
	Arm_Count = 0;
	Part_Count = 0;
	for Object in self.detectionData:

		if( Object[2] == 17 );
				
			__gate.append(Object);
			Arm_Count  +=1;
			Part_Count +=1;

		if( Object[2] == 18 ):
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

		if(  __gate[0][2] == 18):
			self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[1][2],__gate[2][2]);
		elif(__gate[1][2] == 18):
			self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[0][2],__gate[2][2]);
		else:
			self.Left_Side, self.Right_Side = Determine_Left_From_Right(__gate[0][2],__gate[1][2]);

	self.UNORDERED_GATE_COMPONENTS = __gate;

#----------------------END----------------------------#


    def Christians_Method(Gate_Side):
	if(self.Arms_In_Sight):
	

		#use data from left to move

	else:
		#Straif Left Around Fixed Point
		#1) Update YAW 
		#2) relativeMoveXYZ
		
#----------------------MAIN_FUNCTION------------------#

    def update(self):
	#---Vizualization Questions---#

	Gate_Vizualization();

	#----Move to Waypoint----#
	if(not self.Waypoint_Reached):
		self.moveToWaypoint(self.finalWaypoint);

	#----Check for Visual, or Waypoint Reached-----#
	if(self.Waypoint_Reached or Gate_In_Sight):
		self.Waypoint_Reached = True;

	if( (Gate_In_Sight is False) and (self.Waypoint_Reached is True) ):
		#REORIENT (*spin*)
		posedata, X, Y, Z, pitch, yaw, roll = self.relativeMoveXYZ([self.orientation + self.position,0,0,0, 45, 0,0);
		self.moveToWaypoint([posedata, X, Y, Z, yaw, pitch, roll]);

	if( (Gate_In_Sight is True) and (self.Waypoint_Reached is True) ):
		#METHOD INPUT-----START:
		Christians_Method(Gate_Side); """Who needs naming conventions anyway..."""
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
