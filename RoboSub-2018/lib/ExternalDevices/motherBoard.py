'''
Copyright 2017, Felipe Jared Guerrero Moreno, All rights reserved.

.. module:: motherBoard
   :synopsis: Contains data packets and response for the boards.


:Author: Felipe Jared Guerrero Moreno <felipejaredgm@gmail.com>
:Date: Created on Jul 14, 2017
:Description: This module sets up communication with the electrical boards.

'''
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
wcbTimer = utilities.Timer()

class motherBoardDataPackets():
    def __init__(self, serialObject):
        '''
        Sends messages to the Motherboard when necessary. 
        The Frame HEX is hard coded and needs to be adjusted if changed.
        '''
        
        self.motherCom = serialObject
         
    def sendWeapon1Command(self):
        messageID = int('0x7A', 0) # 0000 0111 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        
        # Frame hex specific to the Weapon 1 Command.
        byte1 = int('0x0F', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 1 Command message to the Motherboard:", msg
    
    def sendWeapon2Command(self):
        messageID = int(hex(130), 0) # 0000 1000 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x10', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 2 Command message to the Motherboard:", msg
            
    def sendWeapon3Command(self):
        messageID = int(hex(138), 0) # 0000 1000 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x11', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 3 Command message to the Motherboard:", msg
            
    def sendWeapon4Command(self):
        messageID = int(hex(146), 0) # 0000 1001 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x12', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 4 Command message to the Motherboard:", msg
            
    def sendWeapon5Command(self):
        messageID = int(hex(154), 0) # 0000 1001 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x13', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 5 Command message to the Motherboard:", msg
            
    def sendWeapon6Command(self):
        messageID = int(hex(162), 0) # 0000 1010 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x14', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 6 Command message to the Motherboard:", msg
    
    def sendWeapon7Command(self):
        messageID = int(hex(170), 0) # 0000 1010 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x15', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 7 Command message to the Motherboard:", msg
    
    def sendWeapon8Command(self):
        messageID = int(hex(178), 0) # 0000 1011 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x16', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 8 Command message to the Motherboard:", msg
    
    def sendWeapon9Command(self):
        messageID = int(hex(186), 0) # 0000 1011 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x17', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 9 Command message to the Motherboard:", msg
            
    def sendWeapon10Command(self):
        messageID = int(hex(194), 0) # 0000 1100 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x18', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 10 Command message to the Motherboard:", msg
            
    def sendWeapon11Command(self):
        messageID = int(hex(202), 0) # 0000 1100 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x19', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 11 Command message to the Motherboard:", msg
            
    def sendWeapon12Command(self):
        messageID = int(hex(210), 0) # 0000 1101 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x1A', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 12 Command message to the Motherboard:", msg
            
    def sendWeapon13Command(self):
        messageID = int(hex(218), 0) # 0000 1101 1010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x1B', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon 13 Command message to the Motherboard:", msg
        
    def sendSIBPressureRequest(self):
        messageID = int(hex(523), 0) # 0001 1000 1000
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x41', 0)
        byte2 = int('0x70', 0)
        
        packet = [byte0, byte1, byte2]
        #packet = [int('0xee', 0), int('0x41', 0), int('0x70', 0)]
        #print packet
        #print bytearray(packet)
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send SIB Pressure message to the Motherboard:", msg
    
    def sendSIBTempRequest(self):
        messageID = int(hex(531), 0) # 0001 1001 0000
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x42', 0)
        byte2 = int('0x70', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send SIB Temperature message to the Motherboard:", msg
    
    def sendHYDRASRequest(self):
        messageID = int(hex(540), 0) # 0010 0001 1100
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x43', 0)
        byte2 = int('0x90', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send HYDRAS message to the Motherboard:", msg
    
    def sendHYDRASRawRequest(self):
        messageID = int(hex(548), 0) # 0010 0010 0100
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x44', 0)
        byte2 = int('0x90', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send HYDRAS message to the Motherboard:", msg                    
            
            
    def sendWeaponStatusRequest(self):
        messageID = int(hex(626), 0) # 0010 0111 0010
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x4E', 0)
        byte2 = int('0x50', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Weapon Status message to the Motherboard:", msg
            
    def sendBackplaneCurrentRequest(self):
        messageID = int(hex(633), 0) # 0010 0111 1001
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x4F', 0)
        byte2 = int('0x30', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send Backplane Current message to the Motherboard:", msg
			
    def sendBMSVoltageRequest(self):
        messageID = int(hex(641), 0) # 0001 1001 0000
        byte0 = int('0xEE', 0) # Starting byte, EE in hex
        byte1 = int('0x50', 0)
        byte2 = int('0x30', 0)
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(bytearray(packet))            
        except Exception as msg:
            print "Could not send BMS Voltage message to the Motherboard:", msg
    
    
class motherBoardResponse(threading.Thread):
    def __init__(self, serialObject):
        threading.Thread.__init__(self)
        
        self.motherCom = serialObject
        self.motherBoardPackets = motherBoardDataPackets(self.motherCom)
        
        self.requestTime = 0.01
        self.wcbTime = 5
        self.getList = []
        self.runThread = True
                
    def run(self):
        '''
        Obtains DVL data and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            netRequestTimer = requestTimer.netTimer(requestTimer.cpuClockTimeInSeconds())
            wcbRequestTimer = wcbTimer.netTimer(wcbTimer.cpuClockTimeInSeconds())		
            if netRequestTimer >= self.requestTime:
                #print "Start"				
                pass#self.motherBoardPackets.sendSIBPressureRequest()
                #print "End"
                #self.motherBoardPackets.sendSIBTempRequest()
                #self.motherBoardPackets.sendWeaponStatusRequest()
                #self.motherBoardPackets.sendHYDRASRequest()
                #self.motherBoardPackets.sendHYDRASRawDataRequest()
                #self.motherBoardPackets.sendBackplaneCurrentRequest()
                #self.motherBoardPackets.sendWeaponStatusRequest()
                requestTimer.restartTimer()
            if wcbRequestTimer >= 5:
                #self.motherBoardPackets.sendWeapon5Command()# 4 = Torpedo 1, 5 = torpedo 2, 5 = dropper 1, 6 = dropper 2
                #self.motherBoardPackets.sendWeapon4Command()
                wcbTimer.restartTimer()	
            if wcbRequestTimer >= 5:
                pass#self.motherBoardPackets.sendWeapon8Command()   
                	
                
            #print "Sent Request"
            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
                #print "Got Data"
                self.getList.append(dataPacket)
                
                
                
    def unpack(self):
        '''
        Extracts the raw data from the transmission (collects all bytes into array).
        
        **Parameters**: \n
        * **No Input Parameters.**
         
        **Returns**: \n
        * **self.dataPacketIn** - The raw data transmission.\n
        '''
        try:
            if self.motherCom.inWaiting() != 0:
                #print "asdfghjkl"				
                ID = hex(ord(self.motherCom.read()))
                #print ID
                if ID == "0xee":
                    message = [] #Clear list
                    #print "MESSAGE RECEIVED"
                    
                    byte1 = ord(self.motherCom.read()) #0 if using PD4 output format, 1 if using PD5 output format
                    byte2 = ord(self.motherCom.read()) #How many bytes in ensemble
                    
                    #print byte1
                    #print byte2
                    idFrame = (struct.unpack('h', struct.pack('H', byte1 << 3 | byte2 >> 5))[0])
                    #print 'idFrame', idFrame
                    rtr = (struct.unpack('b', struct.pack('B', int('0x01', 0) & byte2 >> 4))[0])
                    #print 'rtr', rtr
                    payloadLength = (struct.unpack('b', struct.pack('B', int('0x0F', 0) & byte2))[0])
                    #print 'payloadLength', payloadLength
                                        
                    #message = ID, rtr, payloadLength
                    payload = []
                    if payloadLength > 0:
                        for x in range(payloadLength):
                            payload.append(ord(self.motherCom.read()))
                    #print payload    
                    if idFrame == 8:#Kill Switch Interrupt
                        message = [idFrame]
                    elif idFrame == 16:# Leak interrupt
                        message = [idFrame]
                    elif idFrame == 24:# Depth interrupt
                        message = [idFrame]
                    elif idFrame == 32:# SIB interrupt
                        message = [idFrame]
                    elif idFrame == 104:# Backplane Current interrupt
                        current = payload[0]
                        message = [idFrame, current]
                    elif idFrame == 112:# AUTONOMOUS MODE
                        message = [idFrame]
                    elif idFrame == 224:# Weapon 1 on
                        message = [idFrame]
                    elif idFrame == 232:# Weapon 2 on
                        message = [idFrame]
                    elif idFrame == 240:# Weapon 3 on
                        message = [idFrame]
                    elif idFrame == 248:# Weapon 4 on
                        message = [idFrame]
                    elif idFrame == 256:# Weapon 5 on
                        message = [idFrame]
                    elif idFrame == 264:# Weapon 6 on
                        message = [idFrame]
                    elif idFrame == 272:# Weapon 7 on
                        message = [idFrame] 
                    elif idFrame == 280:# Weapon 8 on
                        message = [idFrame]
                    elif idFrame == 288:# Weapon 9 on
                        message = [idFrame]
                    elif idFrame == 296:# Weapon 10 on
                        message = [idFrame]
                    elif idFrame == 304:# Weapon 11 on
                        message = [idFrame]
                    elif idFrame == 312:# Weapon 12 on
                        message = [idFrame]
                    elif idFrame == 320:# Weapon 13 on
                        message = [idFrame]
                    elif idFrame == 392:
                         #Byte 2 (bits 0-1) shifted 8 bits left OR Byte 1 (bits 0-7)
                         extPress1 = struct.unpack('H', struct.pack('H', (payload[1] & int('0x03', 0)) << 8 | payload[0]))[0]
                         #Byte 3 (bits 0-3) shifted 6 bits left OR Byte 2 (bits 2-7) shifted 2 bits right
                         extPress2 = struct.unpack('H', struct.pack('H', (payload[2] & int('0xF', 0)) << 6 | payload[1] >> 2))[0]
                         #Byte 4 (bits 0-5) shifted 4 bits left OR Byte 3 (bits 4-7) shifted 4
                         extPress3 = struct.unpack('H', struct.pack('H', (payload[3] & int('0x1F', 0)) << 4 | payload[2] >> 4))[0]
                         #intPress1 = (struct.unpack('H', struct.pack('H', payload[4] | payload[5] << 8 | (int('0xf', 0) & payload[6]) << 16))[0])
                         message = [idFrame, extPress1, extPress2, extPress3]
                    elif idFrame == 400:
                        pass
                        #intPress2 = (struct.unpack('H', struct.pack('H', payload[6] >> 4 | payload[7] << 4 ))[0])
                    elif idFrame == 504:
                        pass
                    elif idFrame == 656:
			print "Got BMS Start Message..."
                        message = [idFrame]
                    elif idFrame == 648:
						firstPart = float(payload[0])
						secondPart = float(payload[1])
						voltage = firstPart + (secondPart/100)
						message = [idFrame, voltage]
                    self.motherCom.flushInput()
                    return message
                
                else:
                    pass#self.motherCom.flushInput()
            else:
                pass#self.motherCom.flushInput()			        
        except Exception as msg:
            print "Can't receive data from Mother Board:", msg
        
            
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
	back = serial.Serial("/dev/ttyUSB18", 9600)
	motherboard = motherboardDataPackets(back)
	motherResponseThread = motherBoardResponse(back)
	motherboad.sendBackplaneCurrentRequest()
	
	while True:
		if motherResponseThread.inWaiting > 0:
			print "Got something from backplane"
	 
