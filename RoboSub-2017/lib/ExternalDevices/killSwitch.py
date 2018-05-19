'''
Jared
'''

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
                    ID = hex(ord(self.arduinoCom.read()))
                    if ID == '0xee':  
                        killToggle = int(self.arduinoCom.readline())
                        cvolt1 = int(self.arduinoCom.readline())
                        cvolt2 = int(self.arduinoCom.readline())
                        cvolt3 = int(self.arduinoCom.readline())
                        cvolt4 = int(self.arduinoCom.readline())
                        voltage = int(self.arduinoCom.readline())
                        current = int(self.arduinoCom.readline())
                        currentDrive = int(self.arduinoCom.readline())
                        temp1 = int(self.arduinoCom.readline())
                        temp2 = int(self.arduinoCom.readline())
                        temp3 = int(self.arduinoCom.readline())
                        self.arduinoCom.flushInput()
                        return [killToggle, voltage, currentDrive]
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
        