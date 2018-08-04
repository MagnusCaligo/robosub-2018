num = "2"

import serial
import sys
import numpy as np
import struct
import glob

if len(sys.argv) < 3:
	print "Usage: testMaestro.py thrusterID thrusterPWM"

print sys.argv

maestro = serial.Serial("/dev/ttyACM"+num, 9600)

thruster = int(sys.argv[1])
pwm = int(sys.argv[2])

thrust = np.interp(pwm,[-100,100],[0,254])

thrust = int(thrust)

maestro.write(bytearray([0xFF, thruster, thrust]))
