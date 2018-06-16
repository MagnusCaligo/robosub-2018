from abstractMission import AbstractMission
import time


class NavigationMission(AbstractMission):
    
    defaultParameters = AbstractMission.defaultParameters + "Test = False\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

    def initalizeOnMissionStart(self):
	AbstractMission.initalizeOnMissionStart(self)

        self.atWaypoint = False #Way of telling if we are within error of the waypoint
        self.atWaypointStartTime = None #Sets the start time from the moment we are at the waypoint so we can stay there for as long as we need to

        self.sentMessage1 = False
	self.atWaypointPreviousTime= None
	self.waypointTimeSum = 0
        

    def update(self):
	atWaypoint = self.moveToWaypoint(self.finalWaypoint)
        if atWaypoint:
            if self.sentMessage1 == False:
                self.writeDebugMessage("At Waypoint")
                self.sentMessage1 = True
		self.atWaypointStartTime = time.time()
            self.atWaypoint = True
        else:
            self.atWaypoint = False
	    self.atWaypointStartTime = None
            self.sentMessage1 = False
            self.atWaypointStartTime = None
        
        if self.atWaypoint == True:
	    if self.atWaypointPreviousTime == None:
		self.atWaypointPreviousTime = time.time()
	    self.waypointTimeSum += time.time() - self.atWaypointPreviousTime
	    self.atWaypointPreviousTime = time.time()	    
            if self.waypointTimeSum  >= int(self.parameters["waitTime"]): 
                self.writeDebugMessage("Finished The Waypoint")
                return 1 #Signal the mission is over
        else:
 	    self.atWaypointPreviousTime = None	
            self.atWaypointStartTime = None

