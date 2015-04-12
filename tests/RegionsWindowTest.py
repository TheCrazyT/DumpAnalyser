import sys
import os
from RegionsWindow import *
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
        self.regions = MarkedRegions()

class RegionsWindowTest(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.regionsWindow = RegionsWindow()
        Globals.DEBUG = True
        Globals.r_searcher = ReferenceSearcher(None)
        Globals.main_window = MainWindowMock()
        Globals.hex_grid = MarkableGridMock()
        assert isinstance(self.regionsWindow.lstRegions,QtWidgets.QListView)

    def testRegionsWindow(self):
        r = MarkedRegion(0x123,10,100)
        r.set_name("test")
        Globals.hex_grid.regions.append(r)
        self.regionsWindow.show(False)
        assert isinstance(self.regionsWindow.lstRegions,QtWidgets.QListWidget)
        item1 = self.regionsWindow.lstRegions.item(0)
        assert isinstance(item1,QtWidgets.QListWidgetItem)
        self.assertEqual(item1.text(),"00000123 [test]")

if __name__ == "__main__":
    unittest.main()
