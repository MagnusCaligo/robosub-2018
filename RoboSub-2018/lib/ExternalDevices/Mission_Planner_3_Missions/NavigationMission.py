from abstractMission import AbstractMission
import time


class NavigationMission(AbstractMission):
    
    defaultParameters = AbstractMission.defaultParameters + "Test = False\n"

    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

        self.atWaypoint = False #Way of telling if we are within error of the waypoint
        self.atWaypointStartTime = None #Sets the start time from the moment we are at the waypoint so we can stay there for as long as we need to

        self.sentMessage1 = False
        

    def update(self):
	atWaypoint = self.moveToWaypoint(self.finalWaypoint)
        if atWaypoint:
            if self.sentMessage1 == False:
                self.writeDebugMessage("At Waypoint")
		print "At Waypoint"
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

