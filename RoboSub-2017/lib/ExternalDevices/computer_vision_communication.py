import zmq
import json

class ComputerVisionComm:
    """
    This class handles the communication between the external device process
    and the computer vision process.

    Client      ----->     Server
    Python      ----->     C++
    """
    def __init__(self):
        self.__parameters = None
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.REQ) # REQ socket for client
        self.__port = "1234"
        self.__socket.connect("tcp://localhost:%s" % self.__port)
        self.poller = zmq.Poller()
        self.poller.register(self.__socket, zmq.POLLIN)
        self.responseMessage = None
        self.isConnected = False
        self.stateIsSending = True
        self.detectionData = {}
        #self.detectionData["classNumbers"] = []

    def setParameters(self, parameters):
        """
        Decodes the parameters dictionary into a json to be easily
        decoded by the c++ process.
        :param parameters: Dictionary containing the parameter name and value
        :return: None
        """
        self.__parameters = json.dumps(parameters)

    def checkConnection(self):
        """
        Called once to check the connection with computer vision process.
        :return: True if connected, else False
        """
        self.__socket.send("hello")
        self.responseMessage = self.__socket.recv()
        if self.responseMessage == "hello":
            self.isConnected = True
            return True
        else:
            self.isConnected = False
            return False

    def sendCheck(self):
        """
        Sends a check string which will ask the computer vision process
        to check that everything is okay.
        :return: True if everything is okay, else False
        """
        self.__socket.send("check")
        self.responseMessage = self.__socket.recv()
        if self.responseMessage != "good":
            #print self.responseMessage
            return False
        else:
            return True


    def sendParameters(self):
        """
        Sends each parameter first by Key, then by Value.
        :return: True if successful, else False
        """
        #print ("Sent parameters")
	if self.stateIsSending:
	        self.__socket.send(self.__parameters)
		self.stateIsSending = False
	
	if self.poller.poll(100):
	        self.responseMessage = self.__socket.recv()
		#print "Got JSON Message"
		self.stateIsSending = True
	else:
		#print "Didn't get a JSON Message"
		pass
	if self.stateIsSending and self.responseMessage != "No Detections":
		#print "Got Detections"
		self.detectionData = json.loads(self.responseMessage)
	if self.responseMessage == "No Detections":
		#print "No Detections"
		self.detectionData = {}
        '''
        This is a dictionary containing:
            classNumbers
            xLocations
            yLocations
            widths
            heights
        And each of these are an array
        '''

if __name__ == "__main__":
    computerVisionComm = ComputerVisionComm()
    guiParams = {'hueMax': 90, 'saturationMax': 5,
            'valueMax': 3, 'hueMin': 4,
            'saturationMin': 5, 'valueMin': 9,
            'cannyMin': 1, 'cannyMax': 2,
            'min_disparity': 11, 'max_disparity': 12,
            'P1': 13, 'P2': 14,
            'confidenceThreshold': 50,
            'sad': 15, 'ct_win_size': 16,
            'hc_win_size': 17, 'bt_clip_value': 18,
            'max_diff': 19, 'uniqueness_ratio': 20,
            'scanlines_mask': 21, 'useNN': 22,
            'useImage': False, 'useVideo': False,'useCameras':True,
            'nnPath': 'c', 'imagePath': 'i', 'frameSkip':'20',
            'videoPath': 'v'}

    while True:
        computerVisionComm.setParameters(guiParams)
        computerVisionComm.sendParameters()
