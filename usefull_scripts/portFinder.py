from serial.tools import list_ports as lp
available_ports = lp.comports()
boards = []
comPortList = {}
             
        
for port in available_ports:
	print port[0]
	print port[1]
	print port[2]
	print ""
	'''
					if port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUT6OLA\\0000':#if port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUT6OLA\\0000':
						print "AHRS 1 located on " + port[2]
						boards.append("AHRS1")
						comPortList["AHRS1"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTG5PLGLA\\0000':#elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTG5PLGLA\\0000':
						print "AHRS 2 located on " + port[2]
						boards.append("AHRS2")
						comPortList["AHRS2"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6001+FTFUUW8DA\\0000':
						print "AHRS 3 located on " + port[2]
						boards.append("AHRS3")
						comPortList["AHRS3"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&1\\0000': # My computer, RoboSub USB 3.0 left, RoboSub USB 3.0 right, RoboSub USB 2.0 inner, RoboSub USB 2.0 outer
						print "PMUD located on " + port[2]
						boards.append("PMUD")
						comPortList["PMUD"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&2\\0000':
						print "AUX located on " + port[2]
						boards.append("AUX")
						comPortList["AUX"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&3\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&3\\0000':
						print "TCB1 located on " + port[2]
						boards.append("TCB1")
						comPortList["TCB1"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&4\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&2&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&3&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&10&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&14&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&6&4\\0000':
						print "TCB2 located on " + port[2]
						boards.append("TCB2")
						comPortList["TCB2"] = port[0]
						elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&1\\0000':
						print "WCB located on " + port[2]
						boards.append("WCB")
						comPortList["WCB"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&2\\0000':
						print "HYDRAS located on " + port[2]
						boards.append("HYDRAS")
						comPortList["HYDRAS"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&1\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&1\\0000':
						print "WCB located on " + port[2]
						boards.append("WCB")
						comPortList["WCB"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&2\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&2\\0000':
						print "HYDRAS located on " + port[2]
						boards.append("HYDRAS")
						comPortList["HYDRAS"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&3\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&3\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&3\\0000':
						print "DIB located on " + port[2]
						boards.append("DIB")
						comPortList["DIB"] = port[0]
					elif port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&4\\0000': #'FTDIBUS\\VID_0403+PID_6011+5&ECB7860&0&10&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&4&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&9&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&5&4\\0000' or port[2] == 'FTDIBUS\\VID_0403+PID_6011+5&1BF0BA15&0&13&4\\0000':
						print "SIB located on " + port[2]
						boards.append("SIB")
						comPortList["SIB"] = port[0]
	'''
