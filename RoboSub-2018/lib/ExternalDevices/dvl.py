'''
Copyright 2017, Felipe Jared Guerrero Moreno, All rights reserved.

.. module:: dvl
   :synopsis: Handles communication with Nortek DVL.
   
:Author: Jared Guerrero <felipejaredgm@gmail.com>
:Date: Created on Jun 28, 2017
:Description: Defines the commands sent to DVL Computer to setup DVL, get feedback, and reset DVL before starting missions.
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
        self.ahrs = 0
        self.distanceToFloor = 0
        self.velocitiesXYZ = [0, 0, 0]  # Velocities for the DVL's coordinate system
        self.velTimesXYZ = [0, 0, 0]  # Time estimate for the velocities
        self.positionA = [0, 0, 0]  # North, East, Down
    
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
                #print SYNC
                if SYNC == "0xa5":

                    header = ord(self.DVLCom.read())  # Use ord when dealing with 1 byte
                    ID = ord(self.DVLCom.read())  # How many bytes in ensemble
                    family = ord(self.DVLCom.read())  # How many bytes in ensemble
                    dataSize = self.DVLCom.read(2)  # Specify number of bytes if greater than 1
                    dataChecksum = self.DVLCom.read(2)  # How many bytes in ensemble
                    headerChecksum = self.DVLCom.read(2)  # How many bytes in ensemble
                    if hex(ID) == "0x1b":  # If this is a Bottom Tracking Message
                        version = ord(self.DVLCom.read())
                        offsetOfData = ord(self.DVLCom.read())
                        serialNumber = self.DVLCom.read(4)
                        year = ord(self.DVLCom.read())
                        month = ord(self.DVLCom.read())
                        day = ord(self.DVLCom.read())
                        hour = ord(self.DVLCom.read())
                        minute = ord(self.DVLCom.read())
                        seconds = ord(self.DVLCom.read())
                        microSec = self.DVLCom.read(2)
                        numberOfBeams = self.DVLCom.read(2)
                        error = self.DVLCom.read(4)
                        status = self.DVLCom.read(4)
                        soundSpeed = self.DVLCom.read(4)
                        temperature = self.DVLCom.read(4)
                        pressure = self.DVLCom.read(4)
                        velBeam0 = self.DVLCom.read(4)
                        velBeam1 = self.DVLCom.read(4)
                        velBeam2 = self.DVLCom.read(4)
                        velBeam3 = self.DVLCom.read(4)
                        disBeam0 = self.DVLCom.read(4)
                        disBeam0 = struct.unpack('<f', disBeam0)
                        disBeam1 = self.DVLCom.read(4)
                        disBeam1 = struct.unpack('<f', disBeam1)
                        disBeam2 = self.DVLCom.read(4)
                        disBeam2 = struct.unpack('<f', disBeam2)
                        disBeam3 = self.DVLCom.read(4)
                        disBeam3 = struct.unpack('<f', disBeam3)
                        self.distanceToFloor = ((disBeam0[0]) + (disBeam1[0]) + (disBeam2[0]) + (disBeam3[0])) / 4
                        fomBeam0 = self.DVLCom.read(4)
                        fomBeam1 = self.DVLCom.read(4)
                        fomBeam2 = self.DVLCom.read(4)
                        fomBeam3 = self.DVLCom.read(4)
                        dt1Beam0 = self.DVLCom.read(4)
                        dt1Beam1 = self.DVLCom.read(4)
                        dt1Beam2 = self.DVLCom.read(4)
                        dt1Beam3 = self.DVLCom.read(4)
                        dt2Beam0 = self.DVLCom.read(4)
                        dt2Beam1 = self.DVLCom.read(4)
                        dt2Beam2 = self.DVLCom.read(4)
                        dt2Beam3 = self.DVLCom.read(4)
                        timeVelEstBeam0 = self.DVLCom.read(4)
                        timeVelEstBeam1 = self.DVLCom.read(4)
                        timeVelEstBeam2 = self.DVLCom.read(4)
                        timeVelEstBeam3 = self.DVLCom.read(4)
                        velX = self.DVLCom.read(4)
                        velX = struct.unpack('<f', velX)
                        self.velocitiesXYZ[0] = velX[0]
                        velY = self.DVLCom.read(4)
                        velY = struct.unpack('<f', velY)
                        self.velocitiesXYZ[1] = velY[0]
                        velZ1 = self.DVLCom.read(4)
                        velZ1 = struct.unpack('<f', velZ1)
                        self.velocitiesXYZ[2] = velZ1[0]
                        velZ2 = self.DVLCom.read(4)
                        fomX = self.DVLCom.read(4)
                        fomY = self.DVLCom.read(4)
                        fomZ1 = self.DVLCom.read(4)
                        fomZ2 = self.DVLCom.read(4)
                        dt1X = self.DVLCom.read(4)
                        dt1Y = self.DVLCom.read(4)
                        dt1Z1 = self.DVLCom.read(4)
                        dt1Z2 = self.DVLCom.read(4)
                        dt2X = self.DVLCom.read(4)
                        dt2Y = self.DVLCom.read(4)
                        dt2Z1 = self.DVLCom.read(4)
                        dt2Z2 = self.DVLCom.read(4)
                        timeVelEstX = self.DVLCom.read(4)
                        timeVelEstX = struct.unpack('<f', timeVelEstX)  #
                        self.velTimesXYZ[0] = timeVelEstX[0]
                        timeVelEstY = self.DVLCom.read(4)
                        timeVelEstY = struct.unpack('<f', timeVelEstY)
                        self.velTimesXYZ[1] = timeVelEstY[0]
                        timeVelEstZ1 = self.DVLCom.read(4)
                        timeVelEstZ1 = struct.unpack('<f', timeVelEstZ1)
                        self.velTimesXYZ[2] = timeVelEstZ1[0]
                        timeVelEstZ2 = self.DVLCom.read(4)
                        #ensemble = self.getDistanceTraveled()

                    return [self.velocitiesXYZ, self.velTimesXYZ]

                else:
                    self.DVLCom.flushInput()

        except Exception as msg:
            print "Can't receive data from DVL:", msg

    def getDistanceTraveled(self):
        '''
        Gets current NED position.

        **Parameters**: \n
        * **No Input Parameters.**

        **Returns**: \n
        * **No Return.**\n
        '''
        # if self.velocitiesXYZ[0] < -30:
        if self.velocitiesXYZ[0] < -32:
            print self.positionA, "Position Unchanged"
            print self.velocitiesXYZ[0], "DVL Error"
            return None
        else:
            degToRad = 3.1415926535 / 180
            velNcompX = self.velocitiesXYZ[0] * round(math.cos(self.ahrs * degToRad))
            velNcompY = self.velocitiesXYZ[1] * round(math.cos((self.ahrs + 90) * degToRad))

            velEcompX = self.velocitiesXYZ[0] * round(math.sin(self.ahrs * degToRad))
            velEcompY = self.velocitiesXYZ[1] * round(math.sin((self.ahrs + 90) * degToRad))

            lastDistanceTraveledN = (velNcompX * self.velTimesXYZ[0]) + (velNcompY * self.velTimesXYZ[1]) * 1000 / 1.74
            lastDistanceTraveledE = (velEcompX * self.velTimesXYZ[0]) + (velEcompY * self.velTimesXYZ[1]) * 1000 / 1.74
            lastDistanceTraveledD = self.velocitiesXYZ[2] * self.velTimesXYZ[2]

            print "HERE"
            print self.positionA
            self.positionA[0] = self.positionA[0] + lastDistanceTraveledN
            print "THERE"
            self.positionA[1] = self.positionA[1] + lastDistanceTraveledE
            self.positionA[2] = self.positionA[2] + lastDistanceTraveledD

            print velNcompX, "m/s NX"
            print velNcompY, "m/s NY"
            print velNcompX + velNcompY, "m/s N Total"
            print velEcompX, "m/s EX"
            print velEcompY, "m/s EY"

            print self.distanceToFloor, "m Up"
            print lastDistanceTraveledN, "m North"
            print lastDistanceTraveledE, "m East"
            print lastDistanceTraveledD, "m Down"

            print self.velTimesXYZ
            print self.velocitiesXYZ
            print self.positionA, "m North, East, Down"
            print "NO ERROR"
            return [self.velocitiesXYZ, self.velTimesXYZ]

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
		

        
