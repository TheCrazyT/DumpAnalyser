import sys
import os
from PropertiesWindow import *
from MarkedRegions import *
from ReferenceSearcher import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import unittest
from PyQt5.QtCore import *

class ModelMock(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

class MainWindowMock:
    def __init__(self):
        self.rva_list = []

    def readPointer(self):
        return 0x432

class MarkableGridMock:
    def __init__(self):
        self.width=32
        self.model = ModelMock()

class PropertiesWindowTest(unittest.TestCase):
    def testPropertiesWindow(self):
        app = QtWidgets.QApplication(sys.argv)
        p = PropertiesWindow()
        Globals.r_searcher = ReferenceSearcher(None)
        region = MarkedRegion(100, 100)
        Globals.main_window = MainWindowMock()
        Globals.hex_grid = MarkableGridMock()
        region.references.append(Reference(0x123456))
        p.show(region,False)

if __name__ == "__main__":
    unittest.main()
