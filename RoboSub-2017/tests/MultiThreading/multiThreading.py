import urllib2

from PyQt4 import QtCore, QtGui

class DownloadThread(QtCore.QThread):
    data_download = QtCore.pyqtSignal(object)

    def __init__(self, url):
        QtCore.QThread.__init__(self)
        self.url = url

    def run(self):
        info = urllib2.urlopen(self.url).info()
        self.data_download.emit('%s\n%s' % (self.url, info))

class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()