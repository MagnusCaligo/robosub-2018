from PyQt4 import QtCore
import movement
import math
import cv2
import numpy as np
import time
import itertools


class AbstractMission(QtCore.QObject):
    
    '''
    The Abstact Mission class that all other mission classes will inhert from.
    Each mission will have a set of parameters including time to finish, HSV values, etc. 
    Each mission also has a success boolean which will let us know if the mission was succsefull
    There is also an executionTask for missions such as the dropper and torpedo board which will trigger
    when the sub is in the correct position 
    '''
    
    '''
    The initalization of the abstract mission class, the self.parameters variable is a dictionary to access all variables,
    i.e. timeTillGiveup, etc. 
    '''
    def __init__(self, parameters):
        QtCore.QObject.__init__(self)
        self.generalWaypoint = [0,0,0,0,0,0]
        self.lastKnownPosition = [0,0,0,0,0,0]
        self.specificWaypoint = None
        
        '''
        This waypoint is used when calculating the relative move. If its None, then we can calculate a new one, if not then we are currently moving to a relative move waypoint
        '''
        self.relativeMoveWaypoint = None
        
        
        self.name = parameters["name"]
        self.generalDistanceError = 1 #How much of a positional error we want 
        self.generalRotationError = 5 #how much of an orientation error we want
        
        self.specificDistanceError = 3 #How much error we want on the specific waypoint
        self.specificRotationError = 5#how much rotation error we want on the specific waypoint
        
        self.resetFlagBoolean = False
        
        self.cameraMatrix = [[808,     0, 404],
                        [   0, 608, 304],
                        [   0,     0,  1.0],]
        #self.parameters contains information specific to that mission, it will be a dictionary for easy reference
        
        
        self.parameters = {}
        
        
        for i,v in parameters.iteritems():
			self.parameters[i] = v
        
        '''
        Key values inside of parameters
        name - The name of the mission
        maxTime - the maximum time for the mission
        missionType - What type of mission it is; saved as a string and in the same format as the missionCommander strings
        DirectionToLook - This is the direction we will look for obstacles, either a -1 for counterCLockwise or 1 for clockwise
        useWaypoint - This value is defaulted at 0... if the user wants to set this mission's general waypoint to be exactly another
                        waypoint, then this value will be the name of that waypoint. This value is used when initalizing the mission in mission_planner
        useKalmanFilter - This value is defaulted to True, but can be set to false to use pure DVL data
        parametersString - This has a bunch of parameters in them in the form of a string taken from Mission Commander, they will be added to the missions in mission_planner
        useLaser - Boolean which defines if we will be using the laser or not for the mission. Defaulted on False
        drivingMode - Whether the sub moves forward or backwards. 0 for forward 1 for backward
        useRelativeWaypoint - whether the general waypoint is just a relative waypoint, defaulted to False
        useRelativeWorld - use relative movement but relative north, east, and up rather than x,y,z
        '''
        
        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 1
        self.parameters["drivingMode"] = 0
        self.parameters["useRelativeWaypoint"] = "False"
        self.parameters["useRelativeWorld"] = "False"
    
        '''
        FLAGS - These flags will let know mission planner know when to move onto the nex step of the mission
        For example, until the sub is at the general waypoint, mission planner won't tell the sub to start looking 
            around for the obstacle
        '''
        
        self.reachedGeneralWaypoint = False
        self.locatedObstacles = False
        self.reachedSpecificWaypoint = False
        self.readyToExecute = False
        self.executed = False
        self.success = False
        
    #These definitions are the functions for every mission that will be called   
    
    def lookForObstacles(self, externalComm, movementCtonroller):
		print "In abstract mision, shouldn't be here"
		return False
       
    def calculateSpecificWaypoint(self, externalComm, movementController):
		print "In abstract mision, shouldn't be here"
		pass
    
    def getExecutionPositionDifference(self, externalComm, movementController):
		print "In abstract mision, shouldn't be here"
		pass
    
    def checkReadyToExecute(self, externalComm, movementController):
		print "In abstract mision, shouldn't be here"
		pass
    
    def executionTask(self, externalComm, movementController):
		print "In abstract mision, shouldn't be here"
		pass
    
    def checkParameters(self, externalComm, movementController):
		print "In abstract mision, shouldn't be here"
		pass
    
    
    
    def writeDebugMessage(self, string):
        self.emit(QtCore.SIGNAL("debugMessage(PyQt_PyObject)"), string)




class NavigationMission(AbstractMission):
    
    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
        self.sent = [False, False]
        self.parameters["drivingMode"] = 0
        self.parameters["waitTime"] = 10
        self.parameters["startTime"] = 0
        self.depthOfObstacle = 6
        
        for key,value in parameters.iteritems():
        	self.parameters[key] = value

    
    def calculateSpecificWaypoint(self, externalComm, movementController):
        if not self.sent[0]:
            self.writeDebugMessage("Calculating specific waypoint...")
            self.sent[0] = True
        self.specificWaypoint = self.generalWaypoint
        return True
    
    def getExecutionPositionDifference(self, externalComm, movementController):
        if not self.sent[1]:
            self.writeDebugMessage("Calculating Execution Difference....")
            self.sent[1] = True
        self.readyToExecute = True
        self.lastKnownPosition = externalComm.position + externalComm.orientation
        return True
        
    def checkReadyToExecute(self, externalComm, movementController):
        self.readyToExecute = True
    
    def executionTask(self, externalComm, movementController):
        self.writeDebugMessage("Executing Navigation Mission")
    
    def checkParameters(self, externalComm, movementController):
        pass
    
    def startComputerVision(self, externalComm, movementController):
        self.locatedObstacles = True
        
    def lookForObstacles(self, externalComm, movementController):
		return True
		




class QualificationGate(AbstractMission):
    
    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
        
        self.parameters["DirectionToLook"] = False
        self.parameters["useWaypoint"] = None
        self.parameters["useKalmanFilter"] = "True"
        self.parameters["useLaser"] = "False"
        self.parameters["drivingMode"] = 0
        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 0
        self.parameters["searchMethod"] = 0

        '''
        Setting up the specific parameters for this mission to their default values.
        '''
    	
    	for i,v in parameters.iteritems():
			#print i, v
			self.parameters[i] = v
        
        self.lookTime = 5
        self.lookStartTime = None
        self.distance = 3
        self.angleChange = 0
        self.needToPointToObstacles = False
        
        
    def lookForObstacles(self, externalComm, movementCtonroller):
		detections = []
		if "classNumbers" in externalComm.detectionData:
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == 7: #Class Number of the Qualification Gate
					detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
        
    
    def getExecutionPositionDifference(self, externalComm, movementController):
        pass
    
    def executionTask(self, externalComm, movementController):
        pass
    
    def checkParameters(self, externalComm, movementController):
        pass


'''
Buoy Mission Parameters
useNueralNetwork - DEFAULT TRUE. Tells whether we should use the neural network for object detection.
If False, then use basic computer vision
colorBuoy - DEFAULT RED. Which buoy do we want to look for.
ramIntoBuoy - DEFAULT FALSE. Whether we want to ram into the buoy
pullBuoy - DEFAULT FALSE. If we want to pull the buoy instead by using the claw
getDistanceAway - DEFAULT TRUE?. This will be a debug parameter that we can set to test movement based off of depth
(either from stereovision, lasers, computer vision, etc).
It will move us x distance away from the buoy so that we can test how accurate our depth perception is.
searchMethod - 0 for turning left and right to search, 1 for strafing left and right
'''
class Buoys(AbstractMission):
    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

        # NOTE: ALL VARIABLES IN PARAMETERS ARE STRINGS.
        '''
        Setting up all the key parameters to their default values.
        '''
        
        self.parameters["DirectionToLook"] = False
        self.parameters["useWaypoint"] = None
        self.parameters["useKalmanFilter"] = "True"
        self.parameters["useLaser"] = "False"
        self.parameters["drivingMode"] = 0
        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 0
        self.parameters["searchMethod"] = 0

        '''
        Setting up the specific parameters for this mission to their default values.
        '''
        self.parameters["useNeuralNetwork"] = "True"
        self.parameters["colorBuoy"] = "red"
        self.parameters["ramIntoBuoy"] = "False"
        self.parameters["pullBuoy"] = "False"
        self.parameters["getDistanceAway"] = 5
        self.parameters["moveTime"] = 5
        
        self.lookTime = 1
        self.lookStartTime = None
        self.distance = 3
        self.angleChange = 0
        self.needToPointToObstacles = False
        self.atBuoyLocation = False
        self.goBackwards = False
        # self.obstacleLastSighting = None
        
        
        self.depthOfObstacle = self.generalWaypoint[2]
        self.center = None
        
        
       
        for i,v in parameters.iteritems():
			#print i, v
			self.parameters[i] = v
        
        self.buoyColorCode = {"red": 0, "Red": 0, "green":1, "Green":1, "yellow":2, "Yellow":2}
        
        self.detections = None
        
        #Buoy Source Points for SolvePNP
        self.src_pts = [(0,0,0),(.58,0,0),(.58,.58,0),(0,.58,0)]
        self.distance = 3 #Distance to strafe by when looking for obstacles
        self.angle = 45 #Angle to rotate by when looking for obstacles
        self.leftOrRight = self.parameters["DirectionToLook"] #False for Left, true for right

    #
    # The 4 basic steps that are used for each mission.
    #

    '''
    1. Figure out where we need to go depending on what buoy we're looking for.
    '''
        
    def lookForObstacles(self, externalComm, movementController):
		detections = []
		if "classNumbers" in externalComm.detectionData:
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == self.buoyColorCode[self.parameters["colorBuoy"]]:
					detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
        
		if self.parameters["useNeuralNetwork"] == "True":
            #Recalculate the relativeMoveWaypoint if either it doesn't exist or if the detection data has changed
			if self.relativeMoveWaypoint == None:
				print "Calculating new relative waypoint"
				
				pose, n, e, u, x, y, z = None, None, None, None, None, None, None
				
				if self.center != None:
					if self.center > 404:
						self.leftOrRight = False
					else:
						self.leftOrRight = True
                
				if self.leftOrRight == False:
					if self.parameters["searchMethod"] == 0:
						#This is the line called as of right now, no others should be being called
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle-externalComm.position[2],0,self.angle,0)
					elif self.parameters["searchMethod"] == 1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				else:
					if self.parameters["searchMethod"] == 0:
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle - externalComm.position[2],0,-self.angle,0)
					elif self.parameters["searchMethod"] ==1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				
				self.relativeMoveWaypoint = [n, e, u, y, x, z]
				self.angleChange += self.angle
				if abs(self.angleChange) > 360:
					self.angleChange %= 360
					self.depthOfObstacle += 1
					if self.depthOfObstacle > 4:
						self.depthOfObstacle = 4
					
				if abs(self.distance) > 18:
					self.distance = 18	
				
			else:
				#This is where the mission checks to see if it has reached the waypoint it wanted
				error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
					0, self.relativeMoveWaypoint[3], 0)[1]
				#print error
				reachedWaypoint = True				
                #Check to see if we are at the correct location
				if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
					pass #Only called if we are at the correct location
					#print "Not there location"
				else:
					reachedWaypoint = False
                
                #Check to see if we are the correct orientation
				if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
					pass #Only called if we are at the correct orientation
					#print "Not there orientation"
				else:
					reachedWaypoint = False

				if reachedWaypoint:
					if self.lookStartTime == None:
						self.lookStartTime = time.time()
					elif time.time() - self.lookStartTime > self.lookTime:
						self.relativeMoveWaypoint = None
						self.lookStartTime = None
                        #If the sub saw a buoy and has finished pointing towards it, then move on to next part of mission
						if self.needToPointToObstacles == True:
							return True
                        
			if len(detections) > 0:
			
				#Get the first detection, there shouldn't be more than one
				detection = detections[0]
		          
		          #These are the image points of the buoy in the image, this will be with the source points to get buoy depth
				img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
		
		          #Fake camera matrix
				cameraMatrix = [[808,     0, 404],
		                      [   0, 608, 304],
		                      [   0,     0,  1.0],]
		
		          #Solve PNP returns the rotation vector and translation vector of the object
				rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
				
				yaw = externalComm.orientation[0]
				pitch = externalComm.orientation[1]
				
				Nc = (tvec[2] * math.cos(math.radians(yaw))) + (tvec[0] * math.cos(math.radians(90 - yaw)))
				Ec = (tvec[2] * math.sin(math.radians(yaw))) + (tvec[0] * math.sin(math.radians(90 - yaw)))
				Uc = (tvec[1] * math.sin(math.radians(90-pitch))) + (tvec[2] * math.sin(math.radians(pitch)))
				
				#print "Up: ", Uc
				
				leg = math.pow(math.pow(tvec[2],2) - math.pow(tvec[0],2),.5)
				angle =45 - math.degrees(math.atan2(Nc, Ec))
				angle = math.degrees(math.atan2(leg, tvec[0]))
				angle = math.degrees(math.acos(tvec[0]/tvec[2]))
				
				#angle = -math.degrees(rvec[0])
				
                #Need to find a better way to get the angle to point at the buoy
				pose, n,e,u,x,y,z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,0,0,0,0)
				
				self.relativeMoveWaypoint = [n,e,u,y,x,z]
				#This value is triggered when the sub sees a buoy, that way it will point towards it 
				self.needToPointToObstacles = True
				self.detections = detections
			else:
				self.needToPointToObstacles = False
                
    '''            
    1.5: After obstacles are located, get semi-close to them using relative move
    '''     
    def calculateSpecificWaypoint(self, externalComm, movementController):
        #print "calculating Specific"
        # Loop while you haven't found the buoy you want, do a variety of
        # strafing, rotating, and checking with the neural network/basic computer vision.
        error = [100, 100, 100, 100, 100, 100]
        detections = []
        if "classNumbers" in externalComm.detectionData:
			length = len(externalComm.detectionData["classNumbers"])
			if len(externalComm.detectionData["xLocations"]) < length:
				if len(externalComm.detectionData["yLocations"]) < length or len(externalComm.detectionData["widths"]) < length or len(externalComm.detectionData["heights"]) < length:
					print "not all the data is here:" 
					print externalComm.detectionData["classNumbers"],externalComm.detectionData["xLocations"],externalComm.detectionData["yLocations"],externalComm.detectionData["widths"],externalComm.detectionData["heights"]
					return False
			try:
				for i,v in enumerate(externalComm.detectionData["classNumbers"]):
					if v == self.buoyColorCode[self.parameters["colorBuoy"]]:
						detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
			except:
				print "Didn't get all CV data: "
				print externalComm.detectionData["classNumbers"],externalComm.detectionData["xLocations"],externalComm.detectionData["yLocations"],externalComm.detectionData["widths"],externalComm.detectionData["heights"]

				return False
        
        
        if self.relativeMoveWaypoint != None:   
			print self.relativeMoveWaypoint
			error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
													0, self.relativeMoveWaypoint[3], 0)[1]		  
													
			#This line checks to see if we have reached the relative waypoint
			reachedWaypoint = True				
               #Check to see if we are at the correct location
			if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
				pass #Only called if we are at the correct location
			else:
				reachedWaypoint = False
                
                #Check to see if we are the correct orientation
			if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
				pass #Only called if we are at the correct orientation
			else:
				reachedWaypoint = False
				
			timeDif = 0
			if self.atBuoyLocation == True:
				timeDif = 10
			if reachedWaypoint == True:
				if self.lookStartTime == None:
					self.lookStartTime = time.time()
				if time.time() - self.lookStartTime > self.lookTime + timeDif:
					self.relativeMoveWaypoint = None
					self.lookStartTime = None
					if self.atBuoyLocation == True:	
						return True
                        
        if len(detections) > 0:
			self.detections = detections
            #Get the first detection, there shouldn't be more than one
			detection = detections[0]
            
			
			#These are the image points of the buoy in the image, this will be with the source points to get buoy depth
			img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]

			#Fake camera matrix
			cameraMatrix = [[808,     0, 404],
						[   0, 608, 304],
						[   0,     0,  1.0],]
  

			#Solve PNP returns the rotation vector and translation vector of the object
			rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
			
			self.center = detection[1] + (detection[3]/2)
			
			rotationDifference = math.degrees(math.atan2(tvec[0], tvec[2]))
            
			if tvec[1] - int(self.parameters["getDistanceAway"]) < 1:
				self.atBuoyLocation = True
            
			goToDepth = 0
			if tvec[1] > .5:
				goToDepth = .5
			elif tvec[1] < -.5:
				goToDepth = -.5
			#print "Distance: ", self.parameters["getDistanceAway"]
			pose, n,e,u,x,y,z = movementController.relativeMove(externalComm.orientation+externalComm.position, None,None,None,None,None,None, tvec[0], tvec[1], tvec[2]- int(self.parameters["getDistanceAway"]), 0,rotationDifference+10,0)
            
      
            
			if not isinstance(n, float):
				n = n[0]  
			if not isinstance(e, float):
				e = e[0] 
			if not isinstance(u, float):
				u = u[0] 
            

			self.relativeMoveWaypoint = [n,e,u,y,x,z]
			#print self.relativeMoveWaypoint
			self.depthOfObstacle = tvec[1] + externalComm.position[2]
			return False
            
            
			#if self.relativeMoveWaypoint == None:
				
			'''
				We lost sight of the obstacle, check locationObstacleLastSeen to see if we can find it again.
				Divide the screen into 9 segments.
				1 2 3
				6 5 4
				7 8 9
				print "Attempting to locate the obstacle from when we last saw it"
				
				if(xLastSighting > 270 & yLastSighting > 405)
					#1 Go up, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,-45,0,0))
				elif((xLastSighting > 270 & x < 539) & yLastSighting > 405)
					#2 Go up
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,0,0,0))
				elif(xLastSighting > 539 & yLastSighting > 405)
					#3 Go up, scan right
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,45,0,0))
				elf(xLastSighting > 539 & (yLastSighting < 405 & yLastSighting > 203))
					#4 Scan right
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,45,0,0))
				elif((xLastSighting > 270 & xLastSighting < 539) & (yLastSighting < 405 & yLastSighting > 203))
					pass #5 semi inconclusive. Scan left and right?
				elif(xLastSighting < 270 & (yLastSighting < 405 & yLastSighting > 203))
					#6 Scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,-45,0,0))
				elif(xLastSighting < 270 & yLastSighting < 203)
					#7 Go down, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,-45,0,0))
				elif((xLastSighting > 270 & x < 539) & yLastSighting < 203)
					#8 Go down
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,0,0,0))
				elif(xLastSighting > 539 & yLastSighting < 203)
					#9 Go down, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,-45,0,0))
				
				# Check if we got any detections
				if(len(detections) != 0)
						self.relativeMoveWaypoint = [n,e,u,y,x,z]
				'''
        else:
			print "detections are empty"
			self.locatedObstacles = False
			self.relativeMoveWaypoint = None
			self.resetFlagBoolean = True
			self.writeDebugMessage("Lost Obstacle Detection, Going Back")
				
				#return False

        


    '''
    2. Is our distance away from the buoy correct or do we need to be closer
    Get the difference between where we are and where we need to be to be close enough to the buoy to ram into it/pull it.
    '''
    def getExecutionPositionDifference(self, externalComm, movementController):
        print "Getting IN execution"
        if self.lookStartTime == None:
            self.lookStartTime = time.time()
			
		
        if time.time() - self.lookStartTime > (self.lookTime + 1):
			if self.goBackwards == False:
				self.goBackwards = True
				self.lookStartTime = time.time()
			else:
				return True
        if self.goBackwards == False:
			movementController.mixedMove(externalComm.orientation + externalComm.position, 30, 0, self.depthOfObstacle-externalComm.position[2], externalComm.orientation[1],externalComm.orientation[0],externalComm.orientation[2], 0)
        else:
			movementController.mixedMove(externalComm.orientation + externalComm.position, -30, 0, self.depthOfObstacle-externalComm.position[2], externalComm.orientation[1],externalComm.orientation[0],externalComm.orientation[2], 0)
		
        return False
        if self.relativeMoveWaypoint == None or self.lookStartTime == None:
        	pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None,None,None,None,None,None, 0,0,1,0,0,0)
         	self.relativeMoveWaypoint = [n,e,u,y,x,z]
         	self.lookStartTime = time.time()
         	
        if time.time() - self.lookStartTime > int(self.parameters["moveTime"]):
        	pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,0,0,0)
        	self.relativeMoveWaypoint = [n,e,u,y,x,z]
        	self.lookStartTime = None
        	return True
        
        if self.relativeMoveWaypoint != None:
        	movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
                                                self.relativeMoveWaypoint[4], self.relativeMoveWaypoint[3], self.relativeMoveWaypoint[5])
        return False
        

    '''
    3. Are we ready to execute the task of ramming into the buoy or pulling it
    This is pretty basic for the buoy mission since not much needs to be prepared.
    '''
    def checkReadyToExecute(self, externalComm, movementController):
        #We are just going to call mix move and calculateSpecificWaypoint already makes sure that we are ready to execute
        return True
    '''
    4. Tell the sub to ram into the buoy or pull the buoy.
    '''
    def executionTask(self, externalComm, movementController):
        self.lastKnownPosition = externalComm.position + externalComm.orientation
        if self.parameters["ramIntoBuoy"] == "True":
            self.ramIntoBuoy()

        if self.parameters["pullBuoy"] == "True":
            self.pullBuoy()

    #
    # Extra helper methods for movement.
    #

    '''
    Use advancedMove() to strafe to the left and right.
    Alternate strafing to the left and then to the right, increasing the multiple by 1 each time.
    Check neural network/comp vision intermittently.
    @param int distance - The distance by which we are multiplying as we move left to right.
    '''
    def strafeLook(self, distance):
        # TODO: get actual poseData here.
        yaw, pitch, roll = 0
        northPosition, eastPosition, upPosition = 0
        self.poseData = [yaw, pitch, roll, northPosition, eastPosition, upPosition]


        '''
        This trig assumes absolute yaw is relative to east, for example:
        North
        |    /
        |  /   70deg
        |/_____ East

        Polar coordinate to cartesian coordinate conversion:
        x = rcos(theta)
        y = rsin(theta)
        distance is the radius, yaw is theta, x is east, y is north
        '''

        eastTranslate = distance * math.cos(yaw)
        northTranslate = distance * math.sin(yaw)

        desiredEastPosition = eastPosition + eastTranslate
        desiredNorthPosition = northPosition + northTranslate

        # Are current east and north differences greater than a tenth of a foot? Are we close enough to our desired position?
        while eastTranslate > 0.1 and northTranslate > 0.1:
            # Possibly replace this advancedMove with the joystick controller version.
            thrusterPWMs, poseDataError, yaw = movement.advancedMove(self.poseData, desiredNorthPosition, desiredEastPosition,
                                                            upPosition, pitch, yaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            eastTranslate, northTranslate = poseDataError[0], poseDataError[2]

            # TODO: check the camera here. If something found, return 1

    '''
    Use advancedMove() to change the orientation of the sub to look around.
    Look left 90, then right 180. Check neural network/comp vision intermittently.
    '''
    def lookLeftRight(self):
        # TODO: get actual poseData here.
        desiredYaw, pitch, roll = 0
        northPosition, eastPosition, upPosition = 0
        self.poseData = [desiredYaw, pitch, roll, northPosition, eastPosition, upPosition]

        # Look left 90 degrees
        yawError = 90.0
        desiredYaw = desiredYaw + yawError

        # Is the current yaw not within 5 degrees of the desired yaw?
        # If the distance is farther away, you want the degree of error to be smaller
        while yawError > 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                            desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

        # TODO: check the camera here. If something found, return 1

        # Now look right 180 degrees
        yawError = -180
        desiredYaw = desiredYaw + yawError

        # Is the current yaw not within 5 degrees of the desired yaw? (negative this time, so greater than is now less than)
        while yawError < 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                            desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

        # TODO: check the camera here. If something found, return
        # Technically don't need to check the camera for the first 90 degrees, but eh might as well just to be safe

        # Look left 90 degrees
        yawError = 90.0
        desiredYaw = desiredYaw + yawError

        # Check if we are close enough to our desired yaw (within 5 degrees)
        while yawError > 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                     desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

            # TODO: check the camera here. If something found, return 1

    '''
    Move the sub into the buoy so that they touch.
    '''
    def ramIntoBuoy(self):
        # TODO: Move a certain amount towards the buoy so that the sub touches it.
        pass

    '''
    Pull the buoy enough so that the ship on the surface moves.
    '''
    def pullBuoy(self):
        # TODO: Use computer vision to check if the claw is hooked onto the buoy.
        # TODO: Once the claw is properly attached, move the sub backwards a certain amount.
        pass



'''
Football Gate Mission Parameters
angle - The angle at which to go through the gate, for style.
distanceToTravel - The distance the sub will go to get through the gate

'''
class FootballGate(AbstractMission):
    
    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)
        
        self.parameters["DirectionToLook"] = False
        self.parameters["useWaypoint"] = None
        self.parameters["useKalmanFilter"] = "True"
        self.parameters["useLaser"] = "False"
        self.parameters["drivingMode"] = 0
        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 0
        self.parameters["searchMethod"] = 0

        '''
        Setting up the specific parameters for this mission to their default values.
        '''
    	
    	self.parameters["angle"] = 180
    	self.parameters["distanceToTravel"] = 5
    	
    	for i,v in parameters.iteritems():
			self.parameters[i] = v
        
        self.lookTime = 3
        self.lookStartTime = None
        self.distance = 3
        self.angle = 45
        
        
        self.armsLocated = 0
        self.arm1Location = [0,0,0]
        self.arm2Location = [0,0,0]
        
        self.armDistance = 5
        self.movingToObstacles = False
        self.numberOfTimesLost = 0
        self.lastDistance = None
        self.middleAvg = None
        self.obstacleDepth = self.generalWaypoint[2]
        
        self.src_pts = [(0,0,0), (8, 0,0), (8, 4,0), (0, 4,0)]
        
        
    def lookForObstacles(self, externalComm, movementController):
		print "in Obstacle Detection"
		detections = []
		if "classNumbers" in externalComm.detectionData:
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == 11: #Class Number of the Qualification Gate
					detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
		while len(detections) > 2:
			maxHeight = 999
			toRemove = None
			for dect in detections:
				if dect[2] < maxHeight:
					maxHeight = dect[2]
					toRemove = dect
			detections.remove(dect)
		
		if len(detections) >= 2:
			self.numberOfTimesLost = 0
			if not detections[0] == None and not detections[1] == None:
				leftDetection = None
				rightDetection = None
				if detections[0][1] < detections[1][1]:
					leftDetection = detections[0]
					rightDetection = detections[1]
				else:
					leftDetection = detections[1]
					rightDetection = detections[0]
				if leftDetection == None or rightDetection == None:
					print "Detections: ", leftDetection, rightDetection
					
					
				detections = [leftDetection, rightDetection]
				self.middleAvg = (leftDetection[1] + rightDetection[2])/2
				
				img_pts= [(detections[0][1], detections[0][2]), (detections[1][1], detections[1][2]), (detections[1][1] + detections[1][3], detections[1][2] + detections[1][4]), (detections[0][1], detections[0][2] + detections[0][4])]
				rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
				print "translation", tvec
				self.lastDistance = tvec[2]
				pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,None, None, None, None, None, None, tvec[0]+5,tvec[1] + 2,tvec[2]-int(self.parameters["getDistanceAway"]),0,0,0)
				self.relativeMoveWaypoint = [n,e,u,y,x,z]
				self.movingToObstacles = True
			#print "rotional", rvec
		elif len(detections) < 2:
			if self.lastDistance != None:
				if self.lastDistance < 5:
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,None, None, None, None, None, None, 0,0,5,0,0,0)
					self.relativeMoveWaypoint = [n,e,u,y,x,z]
				else:
					self.numberOfTimesLost += 1
					if self.numberOfTimesLost >= 5:
						#self.relativeMoveWaypoint = None
						self.movingToObstacles = False
        
		if len(detections) > 0 and False:
			
			while len(detections) < self.armsLocated:
				self.armsLocated -= 1
			for detection in detections: #Since we might see both arms at once, we want to go through the process for all detections
				
				img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]

				#Fake camera matrix
				cameraMatrix = [[808,     0, 404],
                        [   0, 608, 304],
                        [   0,     0,  1.0],]
  
				#Solve PNP returns the rotation vector and translation vector of the object
				rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
				
				self.obstacleDepth = tvec[1] + externalComm.position[2]
				
				if self.armsLocated == 0: #locate first arm
					self.arm1Location = tvec
					self.armsLocated += 1
				elif self.armsLocated == 1:
					sum = 0
					for i,v in enumerate(tvec):
						sum =+ math.pow(v - self.arm1Location[i],2)
					sum = math.pow(sum, .5)
					if sum > self.armDistance: #The new arm detection is greater than 5 feet away from the first arm, so it must be the second arm
						self.arm2Location = tvec
						self.armsLocated +=1
		elif self.relativeMoveWaypoint == None:
			print "Calculating new relative waypoint"
			if self.middleAvg != None:
				if self.middleAvg <= 404:
					self.angle = -abs(self.angle)
				else:
					self.angle = abs(self.angle)
			pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,0,0,self.angle,0)
			self.relativeMoveWaypoint = [n,e,u,y,x,z]
					
		if self.armsLocated == 2:
			xyz = self.arm1Location
			pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,0,0,0)
			self.relativeMoveWaypoint = [n,e,u,y,x,z]
			self.movingToObstacles = True
			
		if self.relativeMoveWaypoint != None:
			#This is where the mission checks to see if it has reached the waypoint it wanted
			error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.obstacleDepth+3,
				self.relativeMoveWaypoint[4], self.relativeMoveWaypoint[3], self.relativeMoveWaypoint[5])[1]
			#print error
			reachedWaypoint = True				
            #Check to see if we are at the correct location
			if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
				pass #Only called if we are at the correct location
			else:
				reachedWaypoint = False
            
            #Check to see if we are the correct orientation
			if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
				pass #Only called if we are at the correct orientation
			else:
				reachedWaypoint = False

			if reachedWaypoint:
				if self.lookStartTime == None:
					self.lookStartTime = time.time()
				elif time.time() - self.lookStartTime > self.lookTime:
					self.relativeMoveWaypoint = None
					self.lookStartTime = None
                    #If the sub saw a buoy and has finished pointing towards it, then move on to next part of mission
					if self.movingToObstacles == True:
						print "Made it to the arm"
						return True
						
			
        	
        

    '''
    1. Go through the gate at the angle desired and for the distance specified.
    '''
    def calculateSpecificWaypoint(self, externalComm, movementController):
        # Save the current orientation of the sub as the direction we are going to pass the gate.
        # TODO: Get the orientation from AHRS
        prevOrientation = 0

        # TODO: Get actual posedata from the ahrs and dvl
        desiredYaw, pitch, roll = 0
        northPosition, eastPosition, upPosition = 0
        poseData = [desiredYaw, pitch, roll, northPosition, eastPosition, upPosition]

        # Use advancedMove() to change the angle of the sub to the one that was passed in.
        yawError = int(self.parameters["angle"])
        desiredYaw = desiredYaw + yawError

        while yawError < 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition,
                                                                            upPosition, pitch, desiredYaw, roll, [0])
            yawError = poseDataError[4]


        # Now lock your orientation, go through the gate at the angle that we saved from currentOrientation.
        distance = int(self.parameters["distanceToTravel"])
        eastTranslate = distance * math.cos(prevOrientation)
        northTranslate = distance * math.sin(prevOrientation)

        desiredEastPosition = eastPosition + eastTranslate
        desiredNorthPosition = northPosition + northTranslate

        # Are current east and north differences greater than a tenth of a foot? Are we close enough to our desired position?
        while eastTranslate > 0.1 and northTranslate > 0.1:
            # Possibly replace this advancedMove with the joystick controller version.
            thrusterPWMs, poseDataError, yaw = movement.advancedMove(self.poseData, desiredNorthPosition,
                                                                     desiredEastPosition, upPosition, pitch, yaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            eastTranslate, northTranslate = poseDataError[0], poseDataError[2]


        # Set these to true to skip over the other parts, since we've already completed our task.
        self.reachedSpecificWaypoint = True
        self.readyToExecute = True
        self.executed = True
        self.success = True
     

class TorpedoBoard(AbstractMission):
	  
	def __init__(self, parameters):
		AbstractMission.__init__(self, parameters)
	  	
		self.torpedoBoardDict = {"squid":0, "Squid":0, "SQUID":0, 
								"tentacle":1, "Tentacle":1, "TENTACLE":1,
								"upperTarget":2, "lowerTarget":3}
	      
		self.parameters["DirectionToLook"] = False
		self.parameters["useWaypoint"] = None
		self.parameters["useKalmanFilter"] = "True"
		self.parameters["useLaser"] = "False"
		self.parameters["drivingMode"] = 0
		self.parameters["startTime"] = 0
		self.parameters["waitTime"] = 0
		self.parameters["searchMethod"] = 0
		self.parameters["useNeuralNetwork"] = "True"
	
		'''
		Setting up the specific parameters for this mission to their default values.
		'''
		self.parameters["getDistanceAway"] = 5
		self.parameters["useLasers"] = False
		self.parameters["torpedoBoard"] = 0
		
		for i,v in parameters.iteritems():
			self.parameters[i] = v
	      
		self.torpedoBoardSrcPts = [(0,0,0), (2,0,0), (2,4,0), (0,4,0)]
		self.torpedoBoardSmallTargetSrcPts = [(0,0,0), (.66,0,0), (.66,.66,0), (0,.66,0)]
		self.torpedoBoardLargeTargetSrcPts = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
		
		self.tentacleCornerDetections = [None,None,None,None]
		self.squidCornerDetections = [None, None, None, None]
	      
	    
		self.leftOrRight = False
		self.center = None
		self.lookTime = 3
		self.lookStartTime = None
		self.distance = 3
		self.angle = 45
		self.angleChange = 0
		self.needToPointToObstacles = False
		self.depthOfObstacle = self.generalWaypoint[2]
		self.goBackwards = False
		self.atObstacles = False
		self.previousAngle = None
		self.torpedoTime = None
		self.firedFirstTorpedo = False
		self.fireCount = 0
		
	def lookForObstacles(self, externalComm, movementController):
		squidDetections = []
		tentacleDetections = []
		cornerDetections = []
		targetDetections = []
		
		if "classNumbers" in externalComm.detectionData:
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == 3: #Class Number of the Squid
					squidDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
				elif v == 4: #tentacleDetection
					tentacleDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
				elif v == 5: #cornerDetections
					cornerDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
				elif v == 6:# targetDetections:
					targetDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
					
		if self.parameters["useNeuralNetwork"] == "True":
            #Recalculate the relativeMoveWaypoint if either it doesn't exist or if the detection data has changed
			if self.relativeMoveWaypoint == None:
				print "Calculating new relative waypoint"
				
				if self.center != None:
					if self.center > 404:
						self.leftOrRight = False
					else:
						self.leftOrRight = True
                
				if self.leftOrRight == False:
					if self.parameters["searchMethod"] == 0:
						#This is the line called as of right now, no others should be being called
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle-externalComm.position[2],0,self.angle,0)
					elif self.parameters["searchMethod"] == 1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				else:
					if self.parameters["searchMethod"] == 0:
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle - externalComm.position[2],0,-self.angle,0)
					elif self.parameters["searchMethod"] ==1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				
				self.relativeMoveWaypoint = [n, e, u, y, x, z]
				self.angleChange += self.angle
				if abs(self.angleChange) > 360:
					self.angleChange %= 360
					self.depthOfObstacle += 1
					if self.depthOfObstacle > 4:
						self.depthOfObstacle = 4
					
				if abs(self.distance) > 18:
					self.distance = 18	
				
			else:
				#This is where the mission checks to see if it has reached the waypoint it wanted
				error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
					0, self.relativeMoveWaypoint[3], 0)[1]
				#print error
				reachedWaypoint = True				
                #Check to see if we are at the correct location
				if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
					pass #Only called if we are at the correct location
					#print "Not there location"
				else:
					reachedWaypoint = False
                
                #Check to see if we are the correct orientation
				if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
					pass #Only called if we are at the correct orientation
					#print "Not there orientation"
				else:
					reachedWaypoint = False

				if reachedWaypoint:
					if self.lookStartTime == None:
						self.lookStartTime = time.time()
					elif time.time() - self.lookStartTime > self.lookTime:
						self.relativeMoveWaypoint = None
						self.lookStartTime = None
                        #If the sub saw a buoy and has finished pointing towards it, then move on to next part of mission
						if self.needToPointToObstacles == True:
							return True
			
		if len(squidDetections) > 0 or len(tentacleDetections) > 0:
			print "Found torpedo board, moving to them..."
			self.relativeWaypoint = None
			return True
			
	def calculateSpecificWaypoint(self, externalComm, movementController):
		#print "Getting in specific"
		squidDetections = []
		tentacleDetections = []
		cornerDetections = []
		targetDetections = []
		
		try:
			if "classNumbers" in externalComm.detectionData:
				for i,v in enumerate(externalComm.detectionData["classNumbers"]):
					if v == 3: #Class Number of the Squid
						squidDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
					elif v == 4: #tentacleDetection
						tentacleDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
					elif v == 5: #cornerDetections
						cornerDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
					elif v == 6:# targetDetections:
						targetDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
		
		except:
			print "Didn't get all computer vision data"
			
		
		if self.relativeMoveWaypoint != None:
			#This is where the mission checks to see if it has reached the waypoint it wanted
			error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle+1,
				0, self.relativeMoveWaypoint[3], 0)[1]
			#print error
			reachedWaypoint = True				
			#Check to see if we are at the correct location
			if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
				pass #Only called if we are at the correct location
				#print "Not there location"
			else:
				reachedWaypoint = False
					
			#Check to see if we are the correct orientation
			if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
				pass #Only called if we are at the correct orientation
				#print "Not there orientation"
			else:
				reachedWaypoint = False
			if reachedWaypoint:
				if self.lookStartTime == None:
					self.lookStartTime = time.time()
				elif time.time() - self.lookStartTime > self.lookTime:
					self.relativeMoveWaypoint = None
					self.lookStartTime = None
		
		if self.relativeMoveWaypoint == None and self.atObstacles == True:
			print "Made it to the torpedo board"
			self.depthOfObstacle = externalComm.position[2]
			return True
		
		
		if len(squidDetections) > 0 or len(tentacleDetections) > 0:
			detections = []
			detection = None
			
			#Tries to get the detection of the desired board, but if it can't it will use the other board
			detections = detections + squidDetections + tentacleDetections
			if self.torpedoBoardDict[self.parameters["torpedoBoard"]] == 0:
				detection = detections[0]
			elif self.torpedoBoardDict[self.parameters["torpedoBoard"]] == 1:
				detection = detections[len(squidDetections)]
			if detection == None:
				print "Something went wrong"
				return False
			
			squidDetection = None
			tentacleDetection = None
			
			squidCenter = ()
			tentacleCenter = ()
			
			'''
			if len(squidDetections) > 0:
				squidDetection = squidDetections[0]
				squidCenter = (squidDetections[1] + (squidDetections[3]/2), squidDetections[2] + (squidDetections[4]/2))
			if len(tentacleDetections) > 0:
				tentacleDetection = tentacleDetections[0]
				tentacleCenter = (tentacleDetections[1] + (tentacleDetections[3]/2), tentacleDetections[2] + (tentacleDetections[4]/2))
			'''
			'''
			#Check every combination of four corners
			if len(cornerDetections) >= 4:
				for combs in itertools.combinations(cornerDetections,4):
					xavg = (combs[0][1] + combs[1][1] + combs[2][1] + combs[3][1] + (combs[0][3] + combs[1][3] + combs[2][3] + combs[2][3])/2)/4
					yavg = (combs[0][2] + combs[1][2] + combs[2][2] + combs[3][2]+ (combs[0][4] + combs[1][4] + combs[2][4] + combs[2][4])/2)/4
					
					range = 30
					if len(squidCenter) > 0:
						if xavg - range <= squidCenter[0] and xavg + range >= squidCenter[0] and yavg - range <= squidCenter[1] and yavg + range >= squidCenter[1]:
							self.squidCornerDetections = combs
					if len(tentacleCenter) > 0:
						if xavg - range <= tentacleCenter[0] and xavg + range >= tentacleCenter[0] and yavg - range <= tentacleCenter[1] and yavg + range >= tentacleCenter[1]:
							self.tentacleCornerDetections = combs
			
			#Check every combination of two corners
			elif len(cornerDetections) >= 2:
				pass
				for combs in itertoolscombinations(cornerDetections, 2):
					xavg = (combs[0][1] + combs[1][1])/4
					yavg = (combs[0][2] + combs[1][2])/4
					
					if xavg - range <= squidCenter[0] and xavg + range >= squidCenter[0]:
						for corns in combs:
							self.squidCornerDetections.append(corns)
				
			if len(self.squidCornerDetections) >=4:
				unsorted = []
				for combs in self.squidCornerDetections:
					unsorted.append(combs)
				self.squidCornerDetections = [squidCenter, squidCenter, squidCenter, squidCenter]
				for combs in unsorted:
					if combs[0] <= self.squidCornerDetections[0][0] and combs[1] <= self.squidCornerDetections[0][1]:
						self.squidCornerDetections[0] = combs
					if combs[0] >= self.squidCornerDetections[0][0] and combs[1] <= self.squidCornerDetections[0][1]:
						self.squidCornerDetections[1] = combs
					if combs[0] >= self.squidCornerDetections[0][0] and combs[1] >= self.squidCornerDetections[0][1]:
						self.squidCornerDetections[2] = combs
					if combs[0] <= self.squidCornerDetections[0][0] and combs[1] >= self.squidCornerDetections[0][1]:
						self.squidCornerDetections[3] = combs
				print "Got Corners: ", self.squidCornerDetections
			'''
			
			
			img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
	
	
			#Solve PNP returns the rotation vector and translation vector of the object
			rvec, tvec = cv2.solvePnP(np.array(self.torpedoBoardSrcPts).astype('float32'), np.array(img_pts).astype('float32'),np.array(self.cameraMatrix).astype('float32'), None)[-2:]
				
			angleDif = math.degrees(math.atan2(tvec[0], tvec[2]))
			
			if angleDif > 1:
				angleDif = 1
			if angleDif < -3:
				angleDif = -3
			
			
			'''
			if ((self.previousAngle <= 0 and angleDif >= 0) or (self.previousAngle >=0 and angleDif <= 0)) and self.previousAngle != None:
				if not abs(angleDif - self.previousAngle) < 3:
					angleDif = 0
			else:
				self.previousAngle = angleDif
			'''
			print angleDif
				
			#print tvec
			if tvec[2] < 8:
				self.atObstacles = True
				#print "Close to the obstacles"
			pose, n, e, u, x,y,z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None,None, tvec[0]+3,tvec[1],tvec[2] - int(self.parameters["getDistanceAway"]), 0, angleDif , 0)
			
			if not isinstance(n, float) and not isinstance(n, int):
				n = n[0]  
			if not isinstance(e, float) and not isinstance(e, int):
				e = e[0] 
			if not isinstance(u, float) and not isinstance(u, int):
				u = u[0] 
			if not isinstance(x, float) and not isinstance(x, int):
				x = x[0]  
			if not isinstance(y, float) and not isinstance(y, int):
				y = y[0] 
			if not isinstance(z, float) and not isinstance(z, int):
				z = z[0] 
				
			self.depthOfObstacle = tvec[1] + externalComm.position[2]
			self.relativeMoveWaypoint = [n,e,u,y,x,z]
			#print self.relativeMoveWaypoint
			
		elif len(squidDetections) <= 0 and len(tentacleDetections) <= 0:
			self.locatedObstacles = False
			self.relativeMoveWaypoint = None
			self.resetFlagBoolean = True
			return False
			
	def getExecutionPositionDifference(self, externalComm, movementController):
		#print "Getting IN execution"
		if self.relativeMoveWaypoint == None:
			pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,0,0,0)
			self.relativeMoveWaypoint = [n,e,u, y,x,z]
		if self.torpedoTime == None:
			self.torpedoTime = time.time()
		if time.time() - self.torpedoTime > 4:
			if self.firedFirstTorpedo == False:
				externalComm.motherPackets.sendWeapon4Command()
				#externalComm.motherPackets.sendWeapon4Command()
				#externalComm.motherPackets.sendWeapon4Command()
				print "Firing First Torpedo"
				self.firedFirstTorpedo = True
				self.torpedoTime = time.time()
			else:
				externalComm.motherPackets.sendWeapon4Command()
				#externalComm.motherPackets.sendWeapon4Command()
				#externalComm.motherPackets.sendWeapon4Command()
				print "Firing Second Torpedo"
				self.fireCount += 1
				if self.fireCount > 4:
					return True
				else:
					self.torpedoTime = time.time()
		error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle+1,
				0, self.relativeMoveWaypoint[3], 0)[1]
		return False
				
	  
	def getExecutionPositionDifferenceOld(self,externalComm, movementController):
		'''
		First we need to get the correct orientation in relation to the board.
		'''
		squidDetections = []
		tentacleDetections = []
		cornerDetections = []
		orientationCorrect = False
		
		if "classNumbers" in externalComm.detectionData:
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == 3: #Class Number of the Squid
					squidDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
				elif v == 4: #tentacleDetection
					tentacleDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
				elif v == 5: #cornerDetections
					cornerDetections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
		
		# Keep moving until orientation is correct.
		while(orientationCorrect == False):
			# If we don't see the torpedo board we want, go back to look for the obstacles.
			if((len(squidDetections) == 0 & self.parameters["torpedoBoard"] == 0) or (len(tentacleDetections) == 0 & self.parameters["torpedoBoard"] == 1)):
				self.locatedObstacles = False
				self.reachedSpecificWaypoint = False
				return False
			
			# Which and how many corner(s) do we have?
			topLeftCorner = None
			topRightCorner = None
			bottomRightCorner = None
			bottomLeftCorner = None
			numOfCorners = 0
			
			if(self.parameters["torpedoBoard"] == 0): #We're looking for the SQUID BOARD
				if(self.squidCornerDetections[0] != None):
					topLeftCorner = squidCornerDetections[0]
					numOfCorners += 1
				if(self.squidCornerDetections[1] != None):
					topRightCorner = squidCornerDetections[1]
					numOfCorners += 1
				if(self.squidCornerDetections[2] != None):
					bottomRightCorner = squidCornerDetections[2]
					numOfCorners += 1
				if(self.squidCornerDetections[3] != None):
					bottomLeftCorner = squidCornerDetections[3]
					numOfCorners += 1
				if(numOfCorners == 1):
					for i in enumerate(self.squidCornerDetections):
						if(self.squidCornerDetections[i] != None):
							if(self.squidCornerDetections[i][0] < 404 & self.squidCornerDetections[i][1] < 304): # Top left quadrant
								pass # MOVE up and left
							if(self.squidCornerDetections[i][0] > 404 & self.squidCornerDetections[i][1] < 304): # Top right quadrant
								pass # MOVE up and right
							if(self.squidCornerDetections[i][0] > 404 & self.squidCornerDetections[i][1] > 304): # Bottom right quadrant
								pass # MOVE down and right
							if(self.squidCornerDetections[i][0] < 404 & self.squidCornerDetections[i][1] > 304): # Bottom left quadrant
								pass # MOVE down and left
				
				elif(numOfCorners <= 3):
					if((topLeftCorner != None & topRightCorner != None) or (bottomLeftCorner != None & bottomRightCorner != None)): # We can see the top half or the bottom half of the board.
						if((topLeftCorner[1] < topRightCorner[1]) or (bottomLeftCorner[1] < bottomRightCorner[1])): # If the y component of the left corner is less than the right corner, then we need to move right
							pass # MOVE RIGHT
						else: # The board is oriented towards the left and we need to move left.
							pass # MOVE LEFT
				
				elif(numOfCorners == 4):
					height = bottomLeftCorner[1] - topLeftCorner[1]
					width = topRightCorner[0] - topLeftCorner[0]
					
					if(height/width > 1.8 & height/width < 2.2):
						# MOVE towards it normally and execute
						orientationCorrect = True
					else:
						while(not(height/width > 1.8 & height/width < 2.2)):
							if(topLeftCorner[1] > topRightCorner[1]):
								pass # MOVE right
								# Check if we've lost sight
							else:
								pass # MOVE left
					
						orientationCorrect = True
							
								
			else: #We're looking for the TENTACLES BOARD
				if(self.tentacleCornerDetections[0] != None):
					topLeftCorner = tentacleCornerDetections[0]
					numOfCorners += 1
				if(self.tentacleCornerDetections[1] != None):
					topRightCorner = tentacleCornerDetections[1]
					numOfCorners += 1
				if(self.tentacleCornerDetections[2] != None):
					bottomRightCorner = tentacleCornerDetections[2]
					numOfCorners += 1
				if(self.tentacleCornerDetections[3] != None):
					bottomLeftCorner = tentacleCornerDetections[3]
					numOfCorners += 1
					
				if(numOfCorners == 1):
					for i in enumerate(self.tentacleCornerDetections):
						if(self.tentacleCornerDetections[i] != None):
							if(self.tentacleCornerDetections[i][0] < 404 & self.tentacleCornerDetections[i][1] > 304): # Top left quadrant
								pass # MOVE up and left
							if(self.tentacleCornerDetections[i][0] > 404 & self.tentacleCornerDetections[i][1] > 304): # Top right quadrant
								pass # MOVE up and right
							if(self.tentacleCornerDetections[i][0] > 404 & self.tentacleCornerDetections[i][1] < 304): # Bottom right quadrant
								pass # MOVE down and right
							if(self.tentacleCornerDetections[i][0] < 404 & self.tentacleCornerDetections[i][1] < 304): # Bottom left quadrant
								pass # MOVE down and left
							
				elif(numOfCorners <= 3):
					width = 0
					height = 0
					
					if((topLeftCorner != None & topRightCorner != None) or (bottomLeftCorner != None & bottomRightCorner != None)): # We can see the top half or the bottom half of the board.
						if((topLeftCorner[1] > topRightCorner[1]) or (bottomLeftCorner[1] > bottomRightCorner[1])): # If the y component of the left corner is higher than the right corner, then we need to move right
							pass # MOVE RIGHT
						else: # The board is oriented towards the left and we need to move left.
							pass # MOVE LEFT
						
				elif(numOfCorners == 4):
					height = topLeftCorner[1] - bottomLeftCorner[1]
					width = topRightCorner[0] - topLeftCorner[0]
					
					# Our desired width of the board is 2 feet, our error is .3 here
					if(abs(2 - (height/2)) < .3):
						# MOVE towards it normally and execute
						orientationCorrect = True
					else:
						while(not(abs(2 - (height/2)) < .3)):
							if(topLeftCorner[1] > topRightCorner[1]):
								pass # MOVE right
							else:
								pass # MOVE left 
					
						orientationCorrect = True
			
	  
	def executionTask(self,externalComm, movementController):
		pass
	  
	def checkParameters(self,externalComm, movementController):
		pass
    
    
class Dropper(AbstractMission):
    
    def __init__(self, parameters):
		AbstractMission.__init__(self, parameters)

        #Setup parameters
		self.parameters["DirectionToLook"] = False
		self.parameters["useWaypoint"] = None
		self.parameters["useKalmanFilter"] = "True"
		self.parameters["useLaser"] = "False"
		self.parameters["drivingMode"] = 0
		self.parameters["startTime"] = 0
		self.parameters["waitTime"] = 0
		self.parameters["searchMethod"] = 0
	
		'''
		Setting up the specific parameters for this mission to their default values.
		'''
		self.parameters["binType"] = 0 #0 is no lid, 1 is with lid
		self.parameters["whichBin"] = "nolid"
		
		for i,v in parameters.iteritems():
			self.parameters[i] = v
			
		self.dropperDictionary = {"noLid": 0, "nolid":0, "NOLID":0,
								"lid":1, "Lid":1, "LID":1}
	      
		self.dropperBinSrcPts = [(0,0,0),(2.0,0),(2,3,0),(0,3,0)]
	      
		self.lookTime = 5
		self.lookStartTime = None
		self.angle = 10
		self.angleChange = 0
		
		self.depthOfObstacle = self.generalWaypoint[2]
    
    
    '''
    1. Figure out where we need to go depending on what buoy we're looking for.
    '''    
    def lookForObstacles(self, externalComm, movementController):
        detections = []
        for i,v in enumerate(externalComm.detectionData["classNumbers"]):
            if v == "dropper":
                detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
            
        
        if self.parameters["useNeuralNetwork"] == "True":
            #Recalculate the relativeMoveWaypoint if either it doesn't exist or if the detection data has changed
            if self.relativeMoveWaypoint == None or self.detections != detections:
                if self.leftOrRight == False:
                   #TODO Call relative move to move left
                   #movementController.relativeMove(externalComm.orientation + externalComm.position, self.distnace, 0, 0, 0,0,0)
                   pass
                else:
                    #TODO Call relative move to the right
                    pass
                self.distance *= -2
                if abs(self.distance) > 18:
                    self.distance = 18
            else:
                error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.relativeMoveWaypoint[2],
                                                self.relativeMoveWaypoint[4], self.relativeMoveWaypoint[3], self.relativeMoveWaypoint[5])[1]
                                                
                #This line checks to see if we have reached the relative waypoint
                #I couldn't think of an easy way to calculate rotation error, so I just stole something from Mission Planner
                if math.sqrt(math.pow(error[0], 2) + math.pow(error[1], 2) + math.pow(error[2], 2)) < self.generalDistanceError:
                    reachedWaypoint = True
                    for n, p in enumerate(externalComm.orientation):
                            if not ((p - self.generalRotationError <= self.relativeMoveWaypoint[n+3]) and (p + self.generalRotationError >= self.relativeMoveWaypoint[n +3])):
                                    reachedWaypoint = False
                    if reachedWaypoint:
                        self.relativeMoveWaypoint = None
                        
        if self.detections == detections:
            pass
        elif len(detections) > 0:
            self.detections = detections
            return True
        else:
            return False
    
    '''            
    1.5: After obstacles are located, get semi-close to them using relative move
    '''     
    def calculateSpecificWaypoint(self, externalComm, movementController):
        # Loop while you haven't found the dropper bin, do a variety of
        # strafing, rotating, and checking with the neural network/basic computer vision.
        
        detections = []
        for i,v in enumerate(externalComm.detectionData["classNumbers"]):
            if v == "Dropper":
                detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
        
        # TODO change this movement to adjust to the way we want to be in relation to the dropper
        if len(detections) > 0 and self.detections == detections and self.relativeMoveWaypoint != None:   
            error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.relativeMoveWaypoint[2],
                                                self.relativeMoveWaypoint[4], self.relativeMoveWaypoint[3], self.relativeMoveWaypoint[5])[1]
                                                
            #This line checks to see if we have reached the relative waypoint
            #I couldn't think of an easy way to calculate rotation error, so I just stole something from Mission Planner
            if math.sqrt(math.pow(error[0], 2) + math.pow(error[1], 2) + math.pow(error[2], 2)) < self.generalDistanceError:
                reachedWaypoint = True
                for n, p in enumerate(externalComm.orientation):
                        if not ((p - self.generalRotationError <= self.relativeMoveWaypoint[n+3]) and (p + self.generalRotationError >= self.relativeMoveWaypoint[n +3])):
                                reachedWaypoint = False
                if reachedWaypoint:
                    self.relativeMoveWaypoint = None
                    return True
                else:
                    return False
                        
        elif len(detections) > 0 and self.relativeMoveWaypoint == None:
            self.detections = detections
            
            #Get the first detection, there shouldn't be more than one
            detection = detections[0]
            
            # TODO Implement the img_pts of the dropper bin corners
            # img_pts = [(detection.x, detection.y), (detection.x + detection.width, detection.y), (detection.x + detection.width, + detection.y + detection.height), (detection.x, detection.y + detection.height)]

            #Fake camera matrix
            cameraMatrix = [[808,     0, 404/2.0],
                        [   0, 608, 304/2.0],
                        [   0,     0,  1.0],]
  
            #Solve PNP returns the rotation vector and translation vector of the object
            rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
            
            print rvec, tvec
            #This is where we would be calling relative move
            #movementController.relativeMove(externalComm.orientation + externalComm.position, tvec[0, tvec[2], tvec[1], rvec[1], 0,0)
            return False
            
        else:
            self.locatedObstacles = False
            self.relativeMoveWaypoint = None
            self.resetFlagBoolean = True
            self.writeDebugMessage("Lost Obstacle Detection, Going Back")
            return False
    
    def getExecutionPositionDifference(self,externalComm, movementController):
        pass
    
    def executionTask(self, externalComm, movementController):
        if parameters["spiralLook"] is "True":
            print "TODO Implement spiral movement"
        elif parameters["orientLook"] is "True":
            print "TODO Implement Orient with control System"
        pass
    
    def checkParameters(self, externalComm, movementController):
        pass
    
    
class Octogon(AbstractMission):
    
    def __init__(self, parameters):
        AbstractMission.__init__(self, parameters)

        # NOTE: ALL VARIABLES IN PARAMETERS ARE STRINGS.
        '''
        Setting up all the key parameters to their default values.
        '''
        
        self.parameters["DirectionToLook"] = False
        self.parameters["useWaypoint"] = None
        self.parameters["useKalmanFilter"] = "True"
        self.parameters["useLaser"] = "False"
        self.parameters["drivingMode"] = 0
        self.parameters["startTime"] = 0
        self.parameters["waitTime"] = 0
        self.parameters["searchMethod"] = 0

        '''
        Setting up the specific parameters for this mission to their default values.
        '''
        self.parameters["useNeuralNetwork"] = "True"
        self.parameters["colorBuoy"] = "red"
        self.parameters["ramIntoBuoy"] = "False"
        self.parameters["pullBuoy"] = "False"
        self.parameters["getDistanceAway"] = 5
        self.parameters["moveTime"] = 5
        self.parameters["useHydras"] = True
        
        self.lookTime = 1
        self.lookStartTime = None
        self.distance = 3
        self.angleChange = 0
        self.needToPointToObstacles = False
        self.atBuoyLocation = False
        self.goBackwards = False
        self.pingerDetectedForward = False
        # self.obstacleLastSighting = None
        
        
        self.depthOfObstacle = self.generalWaypoint[2]
        self.center = None
        
        
       
        for i,v in parameters.iteritems():
			#print i, v
			self.parameters[i] = v
        
        self.buoyColorCode = {"red": 0, "Red": 0, "green":1, "Green":1, "yellow":2, "Yellow":2}
        #self.HydrasCode = {ADAM WHAT DO)
        
        self.detections = None
        
        #Buoy Source Points for SolvePNP
        self.src_pts = [(0,0,0),(.58,0,0),(.58,.58,0),(0,.58,0)]
        self.distance = 3 #Distance to strafe by when looking for obstacles
        self.angle = 45 #Angle to rotate by when looking for obstacles
        self.leftOrRight = self.parameters["DirectionToLook"] #False for Left, true for right

    #
    # The 4 basic steps that are used for each mission.
    #

    '''
    1. Figure out where we need to go depending on what buoy we're looking for.
    '''
        
    def lookForObstacles(self, externalComm, movementController):
		detections = []
		if "classNumbers" in externalComm.detectionData:#Replace with torped
			for i,v in enumerate(externalComm.detectionData["classNumbers"]):
				if v == self.buoyColorCode[self.parameters["colorBuoy"]]:
					detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
        
		if self.parameters["useNeuralNetwork"] == "True":
            #Recalculate the relativeMoveWaypoint if either it doesn't exist or if the detection data has changed
			if self.relativeMoveWaypoint == None:
				print "Calculating new relativo boardse waypoint"
				
				pose, n, e, u, x, y, z = None, None, None, None, None, None, None
				
				if (externalComm.hydrasHeading > 15) and (externalComm.hydrasHeading < -15): #Pinger is within 15 degrees of current heading
					self.pingerDetectedForward = True
				elif externalComm.hydrasHeading > 15: #Pinger is greater than 15 degrees clockwise from current yaw
					self.leftOrRight = True
				elif externalComm.hydrasHeading < -15:#Pinger is greater than 15 degrees counter-clockwise from current yaw
					self.leftOrRight = False
					
				if self.center != None:
					if self.center > 404:
						self.leftOrRight = False
					else:
						self.leftOrRight = True
                
				if self.leftOrRight == False:
					if self.parameters["searchMethod"] == 0:
						#This is the line called as of right now, no others should be being called
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle-externalComm.position[2],0,self.angle,0)
					elif self.parameters["searchMethod"] == 1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				else:
					if self.parameters["searchMethod"] == 0:
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,self.depthOfObstacle - externalComm.position[2],0,-self.angle,0)
					elif self.parameters["searchMethod"] ==1:
                        #Call to relative move using x,y,z coordinates rather than N, E, U. Used to strafe to the left
						pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None, None, None, None, None, None, 0,0,0,self.depthOfObstacle,0,0)
					else:
						print "Neither were true"
				
				self.relativeMoveWaypoint = [n, e, u, y, x, z]
				self.angleChange += self.angle
				if abs(self.angleChange) > 360:
					self.angleChange %= 360
					self.depthOfObstacle += 1
					if self.depthOfObstacle > 4:
						self.depthOfObstacle = 4
					
				if abs(self.distance) > 18:
					self.distance = 18	
				
			else:
				#This is where the mission checks to see if it has reached the waypoint it wanted
				error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
					0, self.relativeMoveWaypoint[3], 0)[1]
				#print error
				reachedWaypoint = True				
                #Check to see if we are at the correct location
				if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
					pass #Only called if we are at the correct location
					#print "Not there location"
				else:
					reachedWaypoint = False
                
                #Check to see if we are the correct orientation
				if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
					pass #Only called if we are at the correct orientation
					#print "Not there orientation"
				else:
					reachedWaypoint = False

				if reachedWaypoint:
					if self.lookStartTime == None:
						self.lookStartTime = time.time()
					elif time.time() - self.lookStartTime > self.lookTime:
						self.relativeMoveWaypoint = None
						self.lookStartTime = None
                        #If the sub saw a buoy and has finished pointing towards it, then move on to next part of mission
						if self.needToPointToObstacles == True:
							return True
                        
			if len(detections) > 0:
			
				#Get the first detection, there shouldn't be more than one
				detection = detections[0]
		          
		          #These are the image points of the buoy in the image, this will be with the source points to get buoy depth
				img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]
		
		          #Fake camera matrix
				cameraMatrix = [[808,     0, 404],
		                      [   0, 608, 304],
		                      [   0,     0,  1.0],]
		
		          #Solve PNP returns the rotation vector and translation vector of the object
				rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
				
				yaw = externalComm.orientation[0]
				pitch = externalComm.orientation[1]
				
				Nc = (tvec[2] * math.cos(math.radians(yaw))) + (tvec[0] * math.cos(math.radians(90 - yaw)))
				Ec = (tvec[2] * math.sin(math.radians(yaw))) + (tvec[0] * math.sin(math.radians(90 - yaw)))
				Uc = (tvec[1] * math.sin(math.radians(90-pitch))) + (tvec[2] * math.sin(math.radians(pitch)))
				
				#print "Up: ", Uc
				
				leg = math.pow(math.pow(tvec[2],2) - math.pow(tvec[0],2),.5)
				angle =45 - math.degrees(math.atan2(Nc, Ec))
				angle = math.degrees(math.atan2(leg, tvec[0]))
				angle = math.degrees(math.acos(tvec[0]/tvec[2]))
				
				#angle = -math.degrees(rvec[0])
				
                #Need to find a better way to get the angle to point at the buoy
				pose, n,e,u,x,y,z = movementController.relativeMove(externalComm.orientation + externalComm.position, 0,0,0,0,0,0)
				
				self.relativeMoveWaypoint = [n,e,u,y,x,z]
				#This value is triggered when the sub sees a buoy, that way it will point towards it 
				self.needToPointToObstacles = True
				self.detections = detections
			else:
				self.needToPointToObstacles = False
                
    '''            
    1.5: After obstacles are located, get semi-close to them using relative move
    '''     
    def calculateSpecificWaypoint(self, externalComm, movementController):
        #print "calculating Specific"
        # Loop while you haven't found the buoy you want, do a variety of
        # strafing, rotating, and checking with the neural network/basic computer vision.
        error = [100, 100, 100, 100, 100, 100]
        detections = []
        if "classNumbers" in externalComm.detectionData:
			length = len(externalComm.detectionData["classNumbers"])
			if len(externalComm.detectionData["xLocations"]) < length:
				if len(externalComm.detectionData["yLocations"]) < length or len(externalComm.detectionData["widths"]) < length or len(externalComm.detectionData["heights"]) < length:
					print "not all the data is here:" 
					print externalComm.detectionData["classNumbers"],externalComm.detectionData["xLocations"],externalComm.detectionData["yLocations"],externalComm.detectionData["widths"],externalComm.detectionData["heights"]
					return False
			try:
				for i,v in enumerate(externalComm.detectionData["classNumbers"]):
					if v == self.buoyColorCode[self.parameters["colorBuoy"]]:
						detections.append([externalComm.detectionData["classNumbers"][i], externalComm.detectionData["xLocations"][i],externalComm.detectionData["yLocations"][i],externalComm.detectionData["widths"][i],externalComm.detectionData["heights"][i]])
			except:
				print "Didn't get all CV data: "
				print externalComm.detectionData["classNumbers"],externalComm.detectionData["xLocations"],externalComm.detectionData["yLocations"],externalComm.detectionData["widths"],externalComm.detectionData["heights"]

				return False
        
        
        if self.relativeMoveWaypoint != None:   
			print self.relativeMoveWaypoint
			error = movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
													0, self.relativeMoveWaypoint[3], 0)[1]		  
													
			#This line checks to see if we have reached the relative waypoint
			reachedWaypoint = True				
               #Check to see if we are at the correct location
			if abs(error[0]) < self.generalDistanceError and abs(error[1]) < self.generalDistanceError and abs(error[2]) < self.generalDistanceError:
				pass #Only called if we are at the correct location
			else:
				reachedWaypoint = False
                
                #Check to see if we are the correct orientation
			if abs(error[3]) < self.generalRotationError and abs(error[4]) < self.generalRotationError and abs(error[5]) < self.generalRotationError:
				pass #Only called if we are at the correct orientation
			else:
				reachedWaypoint = False
				
			timeDif = 0
			if self.atBuoyLocation == True:
				timeDif = 10
			if reachedWaypoint == True:
				if self.lookStartTime == None:
					self.lookStartTime = time.time()
				if time.time() - self.lookStartTime > self.lookTime + timeDif:
					self.relativeMoveWaypoint = None
					self.lookStartTime = None
					if self.atBuoyLocation == True:	
						return True
                        
        if len(detections) > 0:
			self.detections = detections
            #Get the first detection, there shouldn't be more than one
			detection = detections[0]
            
			
			#These are the image points of the buoy in the image, this will be with the source points to get buoy depth
			img_pts = [(detection[1], detection[2]), (detection[1] + detection[3], detection[2]), (detection[1] + detection[3], + detection[2] + detection[4]), (detection[1], detection[2] + detection[4])]

			#Fake camera matrix
			cameraMatrix = [[808,     0, 404],
						[   0, 608, 304],
						[   0,     0,  1.0],]
  

			#Solve PNP returns the rotation vector and translation vector of the object
			rvec, tvec = cv2.solvePnP(np.array(self.src_pts).astype('float32'), np.array(img_pts).astype('float32'),np.array(cameraMatrix).astype('float32'), None)[-2:]
			
			self.center = detection[1] + (detection[3]/2)
			
			rotationDifference = math.degrees(math.atan2(tvec[0], tvec[2]))
            
			if tvec[1] - int(self.parameters["getDistanceAway"]) < 1:
				self.atBuoyLocation = True
            
			goToDepth = 0
			if tvec[1] > .5:
				goToDepth = .5
			elif tvec[1] < -.5:
				goToDepth = -.5
			#print "Distance: ", self.parameters["getDistanceAway"]
			pose, n,e,u,x,y,z = movementController.relativeMove(externalComm.orientation+externalComm.position, None,None,None,None,None,None, tvec[0], tvec[1], tvec[2]- int(self.parameters["getDistanceAway"]), 0,rotationDifference+10,0)
            
      
            
			if not isinstance(n, float):
				n = n[0]  
			if not isinstance(e, float):
				e = e[0] 
			if not isinstance(u, float):
				u = u[0] 
            

			self.relativeMoveWaypoint = [n,e,u,y,x,z]
			#print self.relativeMoveWaypoint
			self.depthOfObstacle = tvec[1] + externalComm.position[2]
			return False
            
            
			#if self.relativeMoveWaypoint == None:
				
			'''
				We lost sight of the obstacle, check locationObstacleLastSeen to see if we can find it again.
				Divide the screen into 9 segments.
				1 2 3
				6 5 4
				7 8 9
				print "Attempting to locate the obstacle from when we last saw it"
				
				if(xLastSighting > 270 & yLastSighting > 405)
					#1 Go up, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,-45,0,0))
				elif((xLastSighting > 270 & x < 539) & yLastSighting > 405)
					#2 Go up
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,0,0,0))
				elif(xLastSighting > 539 & yLastSighting > 405)
					#3 Go up, scan right
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,-.5,45,0,0))
				elf(xLastSighting > 539 & (yLastSighting < 405 & yLastSighting > 203))
					#4 Scan right
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,45,0,0))
				elif((xLastSighting > 270 & xLastSighting < 539) & (yLastSighting < 405 & yLastSighting > 203))
					pass #5 semi inconclusive. Scan left and right?
				elif(xLastSighting < 270 & (yLastSighting < 405 & yLastSighting > 203))
					#6 Scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,-45,0,0))
				elif(xLastSighting < 270 & yLastSighting < 203)
					#7 Go down, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,-45,0,0))
				elif((xLastSighting > 270 & x < 539) & yLastSighting < 203)
					#8 Go down
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,0,0,0))
				elif(xLastSighting > 539 & yLastSighting < 203)
					#9 Go down, scan left
					pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,.5,-45,0,0))
				
				# Check if we got any detections
				if(len(detections) != 0)
						self.relativeMoveWaypoint = [n,e,u,y,x,z]
				'''
        else:
			print "detections are empty"
			self.locatedObstacles = False
			self.relativeMoveWaypoint = None
			self.resetFlagBoolean = True
			self.writeDebugMessage("Lost Obstacle Detection, Going Back")
				
				#return False

        


    '''
    2. Is our distance away from the buoy correct or do we need to be closer
    Get the difference between where we are and where we need to be to be close enough to the buoy to ram into it/pull it.
    '''
    def getExecutionPositionDifference(self, externalComm, movementController):
        print "Getting IN execution"
        if self.lookStartTime == None:
            self.lookStartTime = time.time()
			
		
        if time.time() - self.lookStartTime > (self.lookTime + 1):
			if self.goBackwards == False:
				self.goBackwards = True
				self.lookStartTime = time.time()
			else:
				return True
        if self.goBackwards == False:
			movementController.mixedMove(externalComm.orientation + externalComm.position, 30, 0, self.depthOfObstacle-externalComm.position[2], externalComm.orientation[1],externalComm.orientation[0],externalComm.orientation[2], 0)
        else:
			movementController.mixedMove(externalComm.orientation + externalComm.position, -30, 0, self.depthOfObstacle-externalComm.position[2], externalComm.orientation[1],externalComm.orientation[0],externalComm.orientation[2], 0)
		
        return False
        if self.relativeMoveWaypoint == None or self.lookStartTime == None:
        	pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position, None,None,None,None,None,None, 0,0,1,0,0,0)
         	self.relativeMoveWaypoint = [n,e,u,y,x,z]
         	self.lookStartTime = time.time()
         	
        if time.time() - self.lookStartTime > int(self.parameters["moveTime"]):
        	pose, n, e, u, x, y, z = movementController.relativeMove(externalComm.orientation + externalComm.position,0,0,0,0,0,0)
        	self.relativeMoveWaypoint = [n,e,u,y,x,z]
        	self.lookStartTime = None
        	return True
        
        if self.relativeMoveWaypoint != None:
        	movementController.advancedMove(externalComm.orientation + externalComm.position, self.relativeMoveWaypoint[0], self.relativeMoveWaypoint[1], self.depthOfObstacle,
                                                self.relativeMoveWaypoint[4], self.relativeMoveWaypoint[3], self.relativeMoveWaypoint[5])
        return False
        

    '''
    3. Are we ready to execute the task of ramming into the buoy or pulling it
    This is pretty basic for the buoy mission since not much needs to be prepared.
    '''
    def checkReadyToExecute(self, externalComm, movementController):
        #We are just going to call mix move and calculateSpecificWaypoint already makes sure that we are ready to execute
        return True
    '''
    4. Tell the sub to ram into the buoy or pull the buoy.
    '''
    def executionTask(self, externalComm, movementController):
        self.lastKnownPosition = externalComm.position + externalComm.orientation
        if self.parameters["ramIntoBuoy"] == "True":
            self.ramIntoBuoy()

        if self.parameters["pullBuoy"] == "True":
            self.pullBuoy()

    #
    # Extra helper methods for movement.
    #

    '''
    Use advancedMove() to strafe to the left and right.
    Alternate strafing to the left and then to the right, increasing the multiple by 1 each time.
    Check neural network/comp vision intermittently.
    @param int distance - The distance by which we are multiplying as we move left to right.
    '''
    def strafeLook(self, distance):
        # TODO: get actual poseData here.
        yaw, pitch, roll = 0
        northPosition, eastPosition, upPosition = 0
        self.poseData = [yaw, pitch, roll, northPosition, eastPosition, upPosition]


        '''
        This trig assumes absolute yaw is relative to east, for example:
        North
        |    /
        |  /   70deg
        |/_____ East

        Polar coordinate to cartesian coordinate conversion:
        x = rcos(theta)
        y = rsin(theta)
        distance is the radius, yaw is theta, x is east, y is north
        '''

        eastTranslate = distance * math.cos(yaw)
        northTranslate = distance * math.sin(yaw)

        desiredEastPosition = eastPosition + eastTranslate
        desiredNorthPosition = northPosition + northTranslate

        # Are current east and north differences greater than a tenth of a foot? Are we close enough to our desired position?
        while eastTranslate > 0.1 and northTranslate > 0.1:
            # Possibly replace this advancedMove with the joystick controller version.
            thrusterPWMs, poseDataError, yaw = movement.advancedMove(self.poseData, desiredNorthPosition, desiredEastPosition,
                                                            upPosition, pitch, yaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            eastTranslate, northTranslate = poseDataError[0], poseDataError[2]

            # TODO: check the camera here. If something found, return 1

    '''
    Use advancedMove() to change the orientation of the sub to look around.
    Look left 90, then right 180. Check neural network/comp vision intermittently.
    '''
    def lookLeftRight(self):
        # TODO: get actual poseData here.
        desiredYaw, pitch, roll = 0
        northPosition, eastPosition, upPosition = 0
        self.poseData = [desiredYaw, pitch, roll, northPosition, eastPosition, upPosition]

        # Look left 90 degrees
        yawError = 90.0
        desiredYaw = desiredYaw + yawError

        # Is the current yaw not within 5 degrees of the desired yaw?
        # If the distance is farther away, you want the degree of error to be smaller
        while yawError > 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                            desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

        # TODO: check the camera here. If something found, return 1

        # Now look right 180 degrees
        yawError = -180
        desiredYaw = desiredYaw + yawError

        # Is the current yaw not within 5 degrees of the desired yaw? (negative this time, so greater than is now less than)
        while yawError < 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                            desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

        # TODO: check the camera here. If something found, return
        # Technically don't need to check the camera for the first 90 degrees, but eh might as well just to be safe

        # Look left 90 degrees
        yawError = 90.0
        desiredYaw = desiredYaw + yawError

        # Check if we are close enough to our desired yaw (within 5 degrees)
        while yawError > 5.0:
            thrusterPWMs, poseDataError, desiredYaw = movement.advancedMove(self.poseData, northPosition, eastPosition, upPosition, pitch,
                                                                     desiredYaw, roll, [0])

            # Get the error values from the returned pose data
            # This is the remaining distance needed to be at the right pose
            yawError = poseDataError[4]

            # TODO: check the camera here. If something found, return 1

    '''
    Move the sub into the buoy so that they touch.
    '''
    def ramIntoBuoy(self):
        # TODO: Move a certain amount towards the buoy so that the sub touches it.
        pass

    '''
    Pull the buoy enough so that the ship on the surface moves.
    '''
    def pullBuoy(self):
        # TODO: Use computer vision to check if the claw is hooked onto the buoy.
        # TODO: Once the claw is properly attached, move the sub backwards a certain amount.
        pass
