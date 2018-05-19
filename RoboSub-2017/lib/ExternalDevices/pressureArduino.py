import serial
import time
import threading
import data_packet_generator
import struct

class pressureArduino:
    def __init__(self, serialObject):
        '''
        **Parameters**: \n
        * **serialObject** - arduino serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.arduinoCom = serialObject
        
        

class pressureResponse(threading.Thread):
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
        while self.runThread:
            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
                self.getList.append(dataPacket)
                    
    def unpack(self):
        '''
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw data transmission.\n
        '''
        if self.arduinoCom != None:
            while self.arduinoCom.inWaiting():
                pressureData = 0
                try:
                    #print "Got here 1"
                    pressureData = int(self.arduinoCom.readline())
                    self.arduinoCom.flushInput()
                    #print "got here 2"
                    #depthError = 17.8 #Depth errror, needs to be changed per pool... Lowering the number makes the sub think its starting lower               
                    #depth = (((pressureData/1023.0)*30.0)-depthError)/(0.466) 
                    depth = (pressureData-600)/11.6
                    #print "got here 3"
                    return depth
                except:
                    #print "Could not print data from Pressure Sensor Arduino"
                    return None
        
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False     
        
