import serial
import time
import threading
import data_packet_generator
import struct

class displayArduino:
    def __init__(self, serialObject):
        '''
        **Parameters**: \n
        * **serialObject** - arduino serial object.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.arduinoCom = serialObject
        
    
    def sendToDisplay(self, data):
        '''
        Send Sub data to dot matrix display using an indexing and comman-seprated-values structure of strings.
        **Parametrs**:
        * **data** - A list containing the sub data to display
        **Returns**:
        * **No Return.**
        '''
        #For each string of data in the data list, write the data to the arduino display
        for index, dataString in enumerate(data):
            #Note: The index for each piece of data is 2 bytes(this is how the arduino reads the index)
            #Single integer indices needed to by augmented with a preceding '0' to be a 2byte string
            if index < 10:
                print(bytes('0'+str(index)+dataString+',', 'ascii'))
                self.arduinoCom.write(bytes('0'+str(index)+dataString+',', 'ascii'))
            else:
                self.arduinoCom.write(bytes(str(index)+dataString+',', 'ascii'))
        #Flush data sending buffer
        self.arduinoCom.flush()
        

class displayResponse(threading.Thread):
    def __init__(self, serialObject):
        '''
        Initializes the thread (starts thread process).
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        threading.Thread.__init__(self)
        
        self.arduinoCom = serialObject
        
        self.runThread = True
        
        self.getList = []
    
    def run(self):
        '''
        
        **Parameters**: \n
        * **No Input Parameters** 
        
        **Return**: \n
        * **No Return.**\n
        '''

    def killThread(self):
        '''
        Ends thread process. 
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.runThread = False     
        
