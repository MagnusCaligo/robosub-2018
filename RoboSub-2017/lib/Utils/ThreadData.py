import Queue
import time
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class InnerLayerThread(QtCore.QThread):

    class Data:
        def __init__(self, command=None, data=None):
            self.command = command
            self.values = data

    """
    Creates a thread.
    """
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.tasks = Queue.Queue()
        print "Created thread."

    def addTask(self, task):
        self.tasks.put(task)

    def run(self):
        while True:
            time.sleep(0.01)
            while self.tasks.empty() == False:
                activeTask = self.tasks.get()
                if activeTask.command == "Default":
                    print "Running default command"

        time.sleep(0.01)


class ThreadUtilities:
    def __init__(self, worker_thread):
        self.worker_thread = worker_thread

    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

            self.signalStatus.emit('Idle.')
            self.worker_thread.start()

    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
