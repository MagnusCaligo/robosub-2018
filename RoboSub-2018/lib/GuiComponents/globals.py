"""
This file will handle all the global variables that the GUI and the
external device process needs to access.  This file will allow all classes, on creation,
restore their variables from here.  The previous state logging system will read a saved
variables file and change the variables in this file for the classes to access.  Then,
whenever a class updates a variable that needs to be saved it will modify the variable here as well.

This file will only be used to save variables.  This file is not meant to pass variables between
threads because that will bring a lot of complexity and problems because of data access issues.
"""

GUI_VARIABLES = {}


"""
def __init__(self):
    #self.__gui_variables = {"YawForward": [], "YawBackward": [], "Pitch": [], "Roll": [],
                            #"Depth": [], "XPosition": [], "YPosition": [], "HSVMax": [],
                            #"HSVMin": [], "CannyEdge": [], "StereoVision": []}

    self.__gui_variables = {}

def setGuiVariables(self, dict):
    self.__gui_variables = dict

def getGuiVariables(self):
    return self.__gui_variables

def setDictValue(self, key, value):
    self.__gui_variables[key] = value

def getDictValue(self, key):
    return self.__gui_variables[key]
"""
