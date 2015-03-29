import sys
import os
from PropertiesWindow import *
from MarkedRegions import *
from ReferenceSearcher import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import unittest

class MainWindowMock:
    def __init__(self):
        self.rva_list = []

    def readPointer(self):
        return 0x432

class PropertiesWindowTest(unittest.TestCase):
    def testPropertiesWindow(self):
        app = QtWidgets.QApplication(sys.argv)
        p = PropertiesWindow()
        Globals.r_searcher = ReferenceSearcher(None)
        region = MarkedRegion(100, 100)
        Globals.main_window = MainWindowMock()
        region.references.append(Reference(0x123456))
        p.show(region,False)

if __name__ == "__main__":
    unittest.main()
