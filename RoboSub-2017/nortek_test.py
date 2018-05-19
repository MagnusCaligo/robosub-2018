'''
Copyright 2017, Felipe Jared Guerrero Moreno, All rights reserved.

.. module:: nortek_test
   :synopsis: Handles communication with Nortek DVL.
   
:Author: Felipe Jared Guerrero Moreno <sdsumechatronics@gmail.com>
:Date: Created on Jun 28, 2017
:Description: Recives and sorts feedback from the Nortek DVL and its proprietary data format, as well as resets the DVL before starting missions.
'''

import serial
import time
import threading
import data_packet_generator
import struct

class DVLDataPackets:
    def __init__(self, serialObject):
        '''
        Initializes the DVL object and sends commands to the DVL computer to set up the DVL.
        
        **Parameters**: \n
        * **serialObject** - DVL serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.DVLCom = serialObject


class DVLResponse(threading.Thread):
    def __init__(self, serialObject):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.DVLCom = serialObject
        
        self.runThread = True
                
        self.alertList = []
        self.getList = []
    
    def run(self):
        '''
        Obtains DVL data and appends it to the instance's list attribute.
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''
        while self.runThread:
            
            #time.sleep(0.01) #Slows down thread to save some power
                
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
            if self.DVLCom.inWaiting() != 0:
                SYNC = hex(ord(self.DVLCom.read()))
                print SYNC
                if SYNC == "0xa5":
                    print SYNC, "start"
                    ensemble = [] #Clear list
                    
                    header = ord(self.DVLCom.read()) #Use ord when dealing with 1 byte
                    print hex(header), "header"
                    ID = ord(self.DVLCom.read()) #How many bytes in ensemble
                    print hex(ID), "ID"
                    family = ord(self.DVLCom.read()) #How many bytes in ensemble
                    print hex(family), "family"
                    dataSize = self.DVLCom.read(2) #Specify number of bytes if greater than 1
                    print struct.unpack('<H', dataSize), "dataSize" #struct.unpack < = Little Endian, H = Unsigned Short, L = Unsigned Short
                    #print (dataSize), "dataSize"
                    dataChecksum = self.DVLCom.read(2)#How many bytes in ensemble
                    print struct.unpack('<H', dataChecksum), "dataChecksum"
                    #print hex(dataChecksum), "dataChecksum"
                    headerChecksum = self.DVLCom.read(2) #How many bytes in ensemble
                    print struct.unpack('<H', headerChecksum), "headerChecksum"
                    #print hex(headerChecksum), "headerChecksum"
                    if hex(ID) == "0x1b":#If this is a Bottom Tracking Message
                        version = ord(self.DVLCom.read())
                        print version, "version" 
                        offsetOfData = ord(self.DVLCom.read())
                        print offsetOfData, "offsetOfData" 
                        serialNumber = self.DVLCom.read(4)
                        print struct.unpack('<I', serialNumber), "serialNumber"
                        #print serialNumber, "serialNumber" 
                        year = ord(self.DVLCom.read())
                        print year, "year" 
                        month = ord(self.DVLCom.read())
                        print month, "month" 
                        day = ord(self.DVLCom.read())
                        print day, "day" 
                        hour = ord(self.DVLCom.read())
                        print hour, "hour" 
                        minute = ord(self.DVLCom.read())
                        print minute, "minute" 
                        seconds = ord(self.DVLCom.read())
                        print seconds, "seconds" 
                        microSec = self.DVLCom.read(2)
                        print struct.unpack('<H', microSec), "microSec"
                        numberOfBeams = self.DVLCom.read(2)
                        print struct.unpack('<H', numberOfBeams), "numberOfBeams"
                        error = self.DVLCom.read(4)
                        print struct.unpack('<L', error), "error"
                        status = self.DVLCom.read(4)
                        print struct.unpack('<L', status), "status"
                        soundSpeed = self.DVLCom.read(4)
                        print struct.unpack('<f', soundSpeed), "soundSpeed"
                        temperature = self.DVLCom.read(4)
                        print struct.unpack('<f', temperature), "temperature"
                        pressure = self.DVLCom.read(4)
                        print struct.unpack('<f', pressure), "pressure"
                        velBeam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', velBeam0), "velBeam0" #m/s
                        velBeam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', velBeam1), "velBeam1" #m/s
                        velBeam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', velBeam2), "velBeam2" #m/s
                        velBeam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', velBeam3), "velBeam3" #m/s
                        disBeam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', disBeam0), "disBeam0" #m Vertical Distance
                        disBeam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', disBeam1), "disBeam1" #m Vertical Distance
                        disBeam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', disBeam2), "disBeam2" #m Vertical Distance
                        disBeam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', disBeam3), "disBeam3" #m Vertical Distance
                        fomBeam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomBeam0), "fomBeam0" #Figure of Merit
                        fomBeam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomBeam1), "fomBeam1" #Figure of Merit
                        fomBeam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomBeam2), "fomBeam2" #Figure of Merit
                        fomBeam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomBeam3), "fomBeam3" #Figure of Merit
                        dt1Beam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Beam0), "dt1Beam0" #
                        dt1Beam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Beam1), "dt1Beam1" #
                        dt1Beam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Beam2), "dt1Beam2" #
                        dt1Beam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Beam3), "dt1Beam3" #
                        dt2Beam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Beam0), "dt2Beam0" #
                        dt2Beam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Beam1), "dt2Beam1" #
                        dt2Beam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Beam2), "dt2Beam2" #
                        dt2Beam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Beam3), "dt2Beam3" #
                        timeVelEstBeam0 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstBeam0), "timeVelEstBeam0" #
                        timeVelEstBeam1 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstBeam1), "timeVelEstBeam1" #
                        timeVelEstBeam2 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstBeam2), "timeVelEstBeam2" #
                        timeVelEstBeam3 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstBeam3), "timeVelEstBeam3" #
                        velX = self.DVLCom.read(4)
                        print struct.unpack('<f', velX), "velX" #
                        velY = self.DVLCom.read(4)
                        print struct.unpack('<f', velY), "velY" #
                        velZ1 = self.DVLCom.read(4)
                        print struct.unpack('<f', velZ1), "velZ1" #
                        velZ2 = self.DVLCom.read(4)
                        print struct.unpack('<f', velZ2), "velZ2" #
                        fomX = self.DVLCom.read(4)
                        print struct.unpack('<f', fomX), "fomX" #
                        fomY = self.DVLCom.read(4)
                        print struct.unpack('<f', fomY), "fomY" #
                        fomZ1 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomZ1), "velZ1" #
                        fomZ2 = self.DVLCom.read(4)
                        print struct.unpack('<f', fomZ2), "fomZ2" #
                        dt1X = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1X), "dt1X" #
                        dt1Y = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Y), "dt1Y" #
                        dt1Z1 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Z1), "dt1Z1" #
                        dt1Z2 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt1Z2), "dt1Z2" #
                        dt2X = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2X), "dt2X" #
                        dt2Y = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Y), "dt2Y" #
                        dt2Z1 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Z1), "dt2Z1" #
                        dt2Z2 = self.DVLCom.read(4)
                        print struct.unpack('<f', dt2Z2), "dt2Z2" #
                        timeVelEstX = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstX), "timeVelEstX" #
                        timeVelEstY = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstY), "timeVelEstY" #
                        timeVelEstZ1 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstZ1), "timeVelEstZ1" #
                        timeVelEstZ2 = self.DVLCom.read(4)
                        print struct.unpack('<f', timeVelEstZ2), "timeVelEstZ2" #
                        
                    #ensemble = [ID, outputFormat, byteNumLSB, byteNumMSB]
                    #for x in range(byteNumMSB << 8 | byteNumLSB):
                    #    ensemble.append(ord(self.DVLCom.read()))
                    
                    return None
                    #return ensemble
                
                else:
                    self.DVLCom.flushInput()
                    
        except Exception as msg:
            print "Can't receive data from DVL:", msg
        
            
    def clearDistanceTraveled(self):
        '''
        Resets the DVL's origin point to its current position.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        pass
        
            
    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False     

if __name__=="__main__":
    #ser = serial.Serial("COM3", 115200) #Tried with and without the last 3 parameters, and also at 1Mbps, same happens.
    #ser.flushInput()
    #ser.flushOutput()
    #while True:
    #    #bytesToRead = ser.inWaiting()
    #    #ser.read(bytesToRead)
    #    data_raw = ser.readline()
    #    print(data_raw)
    DVLComPort = serial.Serial("COM3", 115200)
    #dvlDataPackets = self.DVLDataPackets(DVLComPort)
    dvlResponseThread = DVLResponse(DVLComPort)
    dvlResponseThread.start()
    while len(dvlResponseThread.getList) > 0:
        ensemble = dvlResponseThread.getList.pop(0)
        
        try:
            northPosition = (struct.unpack('i', struct.pack('I', ensemble[61] << 24 | ensemble[60] << 16 | ensemble[59] << 8 | ensemble[58]))[0])*0.00328084 #mm to feet
            eastPosition = (struct.unpack('i', struct.pack('I', ensemble[57] << 24 | ensemble[56] << 16 | ensemble[55] << 8 | ensemble[54]))[0])*0.00328084 #mm to feet
            upPosition = (struct.unpack('i', struct.pack('I', ensemble[65] << 24 | ensemble[64] << 16 | ensemble[63] << 8 | ensemble[62]))[0])*0.00328084 #mm to feet
            positionError = struct.unpack('i', struct.pack('I', ensemble[69] << 24 | ensemble[68] << 16 | ensemble[67] << 8 | ensemble[66]))[0]
            self.position = [northPosition, eastPosition, upPosition, positionError]
            
            xVel = (struct.unpack('h', struct.pack('H', ensemble[6] << 8 | ensemble[5]))[0])*0.00328084 #mm/s to feet/s
            yVel = (struct.unpack('h', struct.pack('H', ensemble[8] << 8 | ensemble[7]))[0])*0.00328084 #mm/s to feet/s
            zVel = (struct.unpack('h', struct.pack('H', ensemble[10] << 8 | ensemble[9]))[0])*0.00328084 #mm/s to feet/s
            self.velocity = [xVel, yVel, zVel] #East, North, Up
            
            heading = (ensemble[53] << 8 | ensemble[52])/100.0
            pitch = struct.unpack('h', struct.pack('H', ensemble[49] << 8 | ensemble[48]))[0]/100.0
            roll = struct.unpack('h', struct.pack('H', ensemble[51] << 8 | ensemble[50]))[0]/100.0
            depth = struct.unpack('h', struct.pack('H', ensemble[47] << 8 | ensemble[46]))[0]/100.0
            self.orientation = [heading, pitch, roll, depth]
            
            elevation = struct.unpack('h', struct.pack('H', ensemble[12] << 8 | ensemble[11]))[0]
            speedOfSound = struct.unpack('h', struct.pack('H', ensemble[42] << 8 | ensemble[41]))[0]
            waterTemp = struct.unpack('h', struct.pack('H', ensemble[44] << 8 | ensemble[43]))[0]/100.0 #deg c
            self.dvlMiscData = [elevation, speedOfSound, waterTemp]
            
        except:
            northPosition, eastPosition, upPosition, positionError = 0, 0, 0, 0
            xVel, yVel, zVel = 0, 0, 0
            heading, pitch, roll, depth = 0, 0, 0, 0
            elevation, speedOfSound, waterTemp = 0, 0, 0
            
        
        #print "Positions(ft) (North, East, Up, Error)", northPosition, eastPosition, upPosition, positionError
        #print "Velocities(ft/s) (X, Y, Z):", xVel, yVel, zVel
        #print "Yaw, Pitch, Roll, Depth (deg, deg, deg, m):", heading, pitch, roll, depth
        #print "Elevation Velocity, Speed Of Sound, Water Temp: (mm/s, m/s, deg C)", elevation, speedOfSound, waterTemp
        #print "\n"
        
        print [self.position, self.velocity, self.orientation, self.dvlMiscData]