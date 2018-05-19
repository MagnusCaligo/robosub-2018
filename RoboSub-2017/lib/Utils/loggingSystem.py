class SubOutputLogging:
    """
    Controls the logging of information for the sub.  This is very
    important because if we do this smart then we run
    simulations offline of the submarines movements and 'thoughts'.
    """
    def __init__(self):
        # Stores all the data output from external devices
        self.external_devices = {'DVL': [], 'AHRS': [], 'PT': []}
        # Stores all the commands send to the sub
        self.command = {'Position': [], 'Thruster': []}
        # The sub will dynamically store the position of the
        # obstacles in relation to it
        self.obstacles = {'Bouy': [], 'Torpedo': []}
        # Stores all the waypoints set by us then all the waypoints
        # set by the sub
        self.waypoints = {'User': [], 'Sub': []}

        self.loggingList = [self.external_devices, self.command,
                            self.obstacles, self.waypoints]
        self.loggingNames = ['External Devices:\n', 'Commands:\n',
                             'Obstacles:\n', 'Waypoints:\n']

        self.writeFile = None
        self.readFile = None


    def setFileName(self, writeFile=None, readFile=None):
        self.writeFile = writeFile
        self.readFile = readFile

    def storeData(self, anyDataDict):
        """
        Stores data into the appropriate dictionary and
        dictionary key.
        :param anyDataDict: Needs to be a dictionary with a 'key'
                            that is listed above with a length of 1
        :return:
        """
        '''
        if len(anyDataDict.keys) > 1:
            print "Dictionary supplied is longer than one key or value. " \
                    "Function must be given a dictionary of length one."
            return
        '''
        # Loop through all the dictionaries to find the
        # matching key of anyDataDict.  Then append the values
        # stored in anyDataDict to the dictionary it matched too
        try:
            for dict in self.loggingList:
                key = anyDataDict.keys()
                key = key[0]
                if dict.has_key(key):
                    dict[key].append(str(anyDataDict[key]))
                    print ("Wrote data.")
        except ValueError as valueError:
            print 'Something wrong with the value of inputted dictionary.', valueError

    def writeToFile(self):
        """
        Opens a file and writes the dictionary data
        to it in the format:

        external_devices:
            DVL: ......
            AHRS: .....

        command:
            Position: .....

        and so on.
        :return:
        """
        # Open file and loop through loggingNames and loggingList
        # simultaneoulsy
        try:
            with open(self.writeFile, 'w+') as f:
                for name, dicts in zip(self.loggingNames, self.loggingList):
                    f.write(name)
                    for key, value in dicts.iteritems():
                        f.write(key + ' ' + str(value) + '\n')
                    f.write('\n')
        except IOError:
            print ("Can't open file.  Need to call setFileName first and"
                   " pass a filename to writeFile.")

    def readFile(self, key):
        """
        Scans through file for a certain key and returns the data
        that belongs to that key.
        :return:
        """
        # Open file and loop through all the lines while
        # storing data in the class instances
        try:
            with open(self.readFile, 'r') as f:
                file_lines = f.readlines()
            #for character in fil


        except IOError:
            print ("Can't open file.  Need to call setFileName first and"
                   " pass a filename to readFile")

class MissionLogging:
    """
    This class will save all variables relevant to a mission.
    The user can then specify what mission they want to load.
    If the user doesn't specify a mission then the latest mission's
    variables will be loaded.
    """
    def __init__(self):
        self.hsvMin = []
        self.hsvMax = []


    