

'''
This is class contains the abstraction of a mission
All missions will look something like this
'''


class AbstractMission():
    def __init__(self, parameters):
        self.generalWaypoint = [0,0,0,0,0,0]
        self.name = parameters["name"]
        
        self.generalDistanceError = 2
        self.generalRotationError = 5

        self.cameraMatrix = [[808, 0, 404],
                            [0,608,304],
                            [0,0,1.0]]
        for i,v in parameters.iteritems():
            self.parameters[i] = v

        '''
        Key values inside of parameters
        name - The name of the mission
        maxTime - the maximum time for the mission
        missionType - What type of mission it is; saved as a string and in the same format as
        DirectionToLook - This is the direction we will look for obstacles, either a -1 for c
        useWaypoint - This value is defaulted at 0... if the user wants to set this mission's
        waypoint, then this value will be the name of that waypoint. This val
        useKalmanFilter - This value is defaulted to True, but can be set to false to use pur
        parametersString - This has a bunch of parameters in them in the form of a string tak
        useLaser - Boolean which defines if we will be using the laser or not for the mission
        drivingMode - Whether the sub moves forward or backwards. 0 for forward 1 for backwar
        useRelativeWaypoint - whether the general waypoint is just a relative waypoint, defau
        useRelativeWorld - use relative movement but relative north, east, and up rather than
        '''

        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 1
        self.parameters["drivingMode"] = 0
        self.parameters["useRelativeWaypoint"] = "False"
        self.parameters["useRelativeWorld"] = "False"

    def update(self):
        pass

    def moveToWaypoint(self, waypoint):
        pass


