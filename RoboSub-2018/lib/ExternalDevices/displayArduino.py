import serial
import time
import threading
import data_packet_generator
import struct

class displayArduino:
    def __init__(self, serialObject):
        '''
        **Parameters**: \n
        * **serialObject** - arduino serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.arduinoCom = serialObject
        
    
    def sendToDisplay(self, depth, waypointN, waypointE, waypointUp, yaw, pitch, roll, mission):
        # Send data to the arduino that controls display inside the sub
            data = "" 
            data = "00=0;01=0;02=0;03=" + thrusterValues + ";04=" + depth + ";05=" + waypointN + ";06=" + waypointE + ";07=" + waypointUp + ";08=" + yaw + ";09=" + pitch + ";10=" + roll + ";11=" + mission
            self.arduinoCom.write(data)
        

class displayResponse(threading.Thread):
    def __init__(self, serialObject):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.arduinoCom = serialObject
        
        self.runThread = True
        
        self.getList = []
    
    def run(self):
        '''
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''

    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False     
        