import datetime
import time
import numpy
import struct
import threading
import math
import data_packet_generator
import lib.Utils.utilities as utilities
import serial

requestTimer = utilities.Timer()

class hydrasBoardDataPackets():
    def __init__(self, serialObject):
        self.hydrasCom = serialObject
    
class hydrasBoardResponseThread(threading.Thread):
    def __init__(self, serialObject):
        threading.Thread.__init__(self)
        
        self.hydrasCom = serialObject
        self.hydrasBoardPackets = hydrasBoardDataPackets(self.hydrasCom)
        
        self.requestTime = 0.3
        self.getList = []
        self.runThread = True
                
    def run(self):
        while self.runThread:
            netRequestTimer = requestTimer.netTimer(requestTimer.cpuClockTimeInSeconds())
            if netRequestTimer >= self.requestTime:
                requestTimer.restartTimer()
                
            #print "Sent Request"
            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
                #print "Got Data"
                self.getList.append(dataPacket)
                
                
                
    def unpack(self):
        '''
        Extracts the raw data from the transmission (collects all bytes into array).
        
        '''
        try:
            #print "hi"
            if self.hydrasCom.inWaiting() != 0:	
                #print "HYDRASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"				
                ID = hex(ord(self.hydrasCom.read()))
                print ID	
                if ID == "0xee" or ID == 3:
                    message = [] #Clear list
                    #print "MESSAGE RECEIVED"
					
                    headingOrPitch = ord(self.hydrasCom.read()) #1 is heading, 2 is pitch
                    error = ord(self.hydrasCom.read()) #If there is error or not
                    #print headingOrPitch
                    #print error
                    if(error == 0) or True:
                        #byte2 = ord(self.hydrasCom.read()) #Time difference
                        #byte3 = ord(self.hydrasCom.read()) #Time difference
                        payload = self.hydrasCom.read(2)
                        byte4 = ord(self.hydrasCom.read()) #End message
                        #print byte2
                        #print byte3
                        # Byte 2              Byte 3
                        # 0000 0000           0000 0000
                        #timeDifference = (struct.unpack('h', struct.pack('H', ((byte2 << 8) & int('0x00', 0)) | byte3))[0])
                        timeDifference = (struct.unpack('>h', payload)[0])  
                        print headingOrPitch, error, timeDifference
						
                        return [headingOrPitch, timeDifference]
                    #else:
                    #    return None
                else:
                    pass
            else:
                pass	        
        except Exception as msg:
            print "Can't receive data from Hydras Board:", msg

    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False    

if __name__ == "__main__":
	back = serial.Serial("/dev/ttyUSB7", 9600)
