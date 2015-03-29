import sys
import os
from PropertiesWindow  import *
from MarkedRegions     import *
from ReferenceSearcher import *
from PyQt5             import QtCore, QtGui, QtWidgets, uic

class MainWindowMock:
    def __init__(self):
        self.rvaList = []
    def readPointer(self):
        return 0x432

if __name__ == "__main__":
    app                = QtWidgets.QApplication(sys.argv)
    p                  = PropertiesWindow()
    Globals.rSearcher  = ReferenceSearcher(None)
    region             = MarkedRegion(100,100)
    Globals.mainWindow = MainWindowMock()
    region.references.append(Reference(0x123456))
    p.show(region)
    sys.exit(0)
