num = "2"

import time
import serial
import sys
import numpy as np
import struct
import glob

maestro = serial.Serial("/dev/ttyACM"+num, 9600)

pwm = 10
thrust = np.interp(pwm,[-100,100],[0,254])

thrust = int(thrust)


for i in range(1,9):
	print "Testing Thruster: ", i
	pwm = 10
	thrust = np.interp(pwm,[-100,100],[0,254])
	thrust = int(thrust)
	maestro.write(bytearray([0xFF, i, thrust]))

	time.sleep(1)

	pwm = 0
	thrust = np.interp(pwm,[-100,100],[0,254])
	thrust = int(thrust)
	maestro.write(bytearray([0xFF, i, thrust]))

