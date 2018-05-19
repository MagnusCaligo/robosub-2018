import serial
import time
import threading
import data_packet_generator
import struct

class BatteryBoard:
	def __init__(self, serialObject):
		'''
		**Parameters**: \n
		* **serialObject** - arduino serial object.
        
		**Returns**: \n
        * **No Return.**\n
        '''
        
		self.batteryBoardCom = serialObject
        
	def requestVoltageData(self):
		pass
	
	def rebootComputer(self):
		pass
        

class batteryBoardResponse(threading.Thread):
    def __init__(self, serialObject):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.batteryBoardCom = serialObject
        
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
        if self.batteryBoardCom != None:
            while self.batteryBoardCom.inWaiting():
                try:
                    self.batteryBoardCom.flushInput()
                    return None
                except:
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
        
