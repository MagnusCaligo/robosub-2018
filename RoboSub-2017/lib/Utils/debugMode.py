from PyQt4 import QtCore


class DebugMode:
    """
    The purpose of this class is to set up timers to run the gui in almost a simulation.
    """
    def __init__(self):
        self.externalDeviceTimer = QtCore.QTimer()