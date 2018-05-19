
'''
This class is designed to takine in our current position and desired position and 
determine how to get there using LQR and by communicating with the thrusters
'''

class NavigationManagmentSystem:
    
    def __init__(self):
        '''
        Initalize Thrusters
        '''
        pass
        
    def beginAutonomousRun(self):
        #Get list of missions to run from Loging System
        #Run each one 
        pass
        

class Thruster:
    
    def __init__(self, id, linearDisplacement, angularDisplacement):
        self.id = id
        self.linearDisplacement = linearDisplacement
        self.angularDisplacement = angularDisplacement
        
    def setDesiredPower(self):
        #value between -100 to 100
        #will be implemented with WBC or arduino
        pass
        
    