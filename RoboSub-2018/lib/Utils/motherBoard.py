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
#import data_packet_generator
import utilities
import serial

requestTimer = utilities.Timer()

class motherBoardDataPackets:
    def __init__(self, serialObject):
        '''
        Sends messages to the Motherboard when necessary. 
        Sends in this format:
        XXXY ZZZZ
        frameID = XXX
        rtr = Y
        payload = ZZZZ
        '''
        
        self.motherCom = serialObject
         
    def sendWeapon1Command(self):
        messageID = hex(122) # 0000 0000 0111 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 1 Command message to the Motherboard:", msg
    
    def sendWeapon2Command(self):
        messageID = hex(82) # 0000 0000 1000 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 2 Command message to the Motherboard:", msg
            
    def sendWeapon3Command(self):
        messageID = hex(138) # 0000 0000 1000 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 3 Command message to the Motherboard:", msg
            
    def sendWeapon4Command(self):
        messageID = hex(146) # 0000 0000 1001 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 4 Command message to the Motherboard:", msg
            
    def sendWeapon5Command(self):
        messageID = hex(154) # 0000 0000 1001 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 5 Command message to the Motherboard:", msg
            
    def sendWeapon6Command(self):
        messageID = hex(162) # 0000 0000 1010 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 6 Command message to the Motherboard:", msg
    
    def sendWeapon7Command(self):
        messageID = hex(170) # 0000 0000 1010 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 7 Command message to the Motherboard:", msg
    
    def sendWeapon8Command(self):
        messageID = hex(178) # 0000 0000 1011 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 8 Command message to the Motherboard:", msg
    
    def sendWeapon9Command(self):
        messageID = hex(186) # 0000 0000 1011 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 9 Command message to the Motherboard:", msg
            
    def sendWeapon10Command(self):
        messageID = hex(194) # 0000 0000 1100 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 10 Command message to the Motherboard:", msg
            
    def sendWeapon11Command(self):
        messageID = hex(202) # 0000 0000 1100 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 11 Command message to the Motherboard:", msg
            
    def sendWeapon12Command(self):
        messageID = hex(210) # 0000 0000 1101 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 12 Command message to the Motherboard:", msg
            
    def sendWeapon13Command(self):
        messageID = hex(218) # 0000 0000 1101 1010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon 13 Command message to the Motherboard:", msg
        
    def sendSIBPressureRequest(self):
        messageID = hex(507) # 0000 0001 1111 1011
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send SIB Pressure message to the Motherboard:", msg
    
    def sendSIBTempRequest(self):
        messageID = hex(515) # 0000 0010 0000 0011
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send SIB Temperature message to the Motherboard:", msg
    
    def sendHYDRASRequest(self):
        messageID = hex(524) # 0000 0010 0000 1100
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send HYDRAS message to the Motherboard:", msg
            
    def sendHYDRASRawDataRequest(self):
        messageID = hex(532) # 0000 0010 0001 0100
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send HYDRAS Raw Data message to the Motherboard:", msg
            
    def sendWeaponStatusRequest(self):
        messageID = hex(610) # 0000 0010 0110 0010
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Weapon Status message to the Motherboard:", msg
            
    def sendBackplaneCurrentRequest(self):
        messageID = hex(617) # 0000 0010 0110 1001
        byte0 = struct.pack('B', hex(238)) # Starting byte, EE in hex
        byte1 = struct.pack('B', hex(255) & messageID >> 3) # Gets XXX portion
        byte2 = struct.pack('B', (hex(224) & messageID << 5) | hex(16)) # Y is 1, and ZZZZ is always 0000 in our case
        
        packet = [byte0, byte1, byte2]
        
        try:
            self.motherCom.write(byteArray(packet))            
        except Exception as msg:
            print "Could not send Backplane Current message to the Motherboard:", msg
    
    
class motherBoardResponse(threading.Thread):
    def __init__(self, serialObject):
        threading.Thread.__init__(self)
        
        self.motherCom = serialObject
        self.motherBoardPackets = motherBoardDataPackets(self.motherCom)
        
        self.requestTime = 0.3
                
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
            if netRequestTimer >= self.requestTime:
                self.motherBoardPackets.sendSIBPressureRequest()
                self.motherBoardPackets.sendSIBTempRequest()
                #self.motherBoardPackets.sendWeaponStatusRequest()
                #self.motherBoardPackets.sendHYDRASRequest()
                #self.motherBoardPackets.sendHYDRASRawDataRequest()
                self.motherBoardPackets.sendBackplaneCurrentRequest()
                #self.motherBoardPackets.sendWeaponStatusRequest()
                requestTimer.restartTimer()
                
            dataPacket = self.unpack() #Reads in data packets
            if dataPacket != None and dataPacket != [0]:
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
                ID = hex(ord(self.motherCom.read()))
                if ID == "0xee":
                    message = [] #Clear list
                    print "MESSAGE RECEIVED"
                    
                    byte1 = ord(self.motherCom.read()) #0 if using PD4 output format, 1 if using PD5 output format
                    byte2 = ord(self.motherCom.read()) #How many bytes in ensemble
                    
                    idFrame = (struct.unpack('h', struct.pack('H', byte1 << 3 | byte2 >> 5))[0])
                    rtr = (struct.unpack('b', struct.pack('B', hex(1) & byte2 >> 4))[0])
                    payloadLength = (struct.unpack('b', struct.pack('B', hex(15) & byte2))[0])
                                        
                    #message = ID, rtr, payloadLength
                    payload = []
                    if payloadLength > 0:
                        for x in range(payloadLength-1):
                            payload.append(ord(self.motherCom.read()))
                    print payload    
                    if idFrame == 8:#Kill Switch Interrupt
                        return [idFrame]
                    elif idFrame == 16:# Leak interrupt
                        pass
                        
                    
                    return message
                
                else:
                    self.motherCom.flushInput()
                    
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
	back = serial.Serial("/dev/ttyUSB7", 9600)
	motherboard = motherBoardDataPackets(back)
	motherboard.sendBackplaneCurrentRequest()
	 
