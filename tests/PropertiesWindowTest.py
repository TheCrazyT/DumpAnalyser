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

def mockedInput(widget,txt,lbl):
    return "Test123",True

class PropertiesWindowTest(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.properties_window = PropertiesWindow()
        Globals.r_searcher = ReferenceSearcher(None)
        Globals.main_window = MainWindowMock()
        Globals.hex_grid = MarkableGridMock()
        Globals.DEBUG = True
        Globals.input = mockedInput

    def testPropertiesWindow(self):
        region = MarkedRegion(100, 100)
        region.set_name("Blubb")
        region.references.append(Reference(0x123456))
        self.properties_window.show(region,False)
        assert isinstance(self.properties_window.tvProps,QtWidgets.QTreeWidget)

        lst_texts = []
        lst_texts.append("References of 00000064 (00000064)")
        lst_texts.append("Pointers of 00000064 (00000064)")
        lst_texts.append("Name: Blubb")

        for i in range(0,len(lst_texts)):
            tli = self.properties_window.tvProps.topLevelItem(i)
            assert isinstance(tli,QtWidgets.QTreeWidgetItem)
            self.assertEqual(tli.text(0),lst_texts[i])

        tli = self.properties_window.tvProps.topLevelItem(2)
        assert isinstance(tli,QtWidgets.QTreeWidgetItem)
        self.properties_window.item_click(tli)
        tli = self.properties_window.tvProps.topLevelItem(2)
        assert isinstance(tli,QtWidgets.QTreeWidgetItem)
        self.assertEqual(tli.text(0),"Name: Test123")


if __name__ == "__main__":
    unittest.main()
