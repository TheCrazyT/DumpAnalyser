import sys
import os
from Globals import dbg
import Globals
from MarkedRegions import MarkedRegion,Reference
from ReferenceSearcher import ReferenceSearcher
from PropertiesWindow import PropertiesWindow
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import unittest
import struct
from PyQt5.QtCore import *

class ModelMock(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

class MainWindowMock:
    def __init__(self):
        self._rva_list = [(0,0,1000)]

    def read_pointer(self,pos):
        assert pos == 0x68
        dbg("read_pointer %08x" % pos)
        return struct.pack("I",0x83)

    def get_rva_list(self):
        return self._rva_list

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
        region = MarkedRegion(0x64, 100)
        region.set_name("Blubb")
        region.references.append(Reference(0x123456))
        region.pointers.append(Reference(0x68))
        self.properties_window.show_refs = True
        self.properties_window.ref = 0x68
        self.properties_window.show(region,False)
        assert isinstance(self.properties_window.tvProps,QtWidgets.QTreeWidget)

        lst_texts = []
        lst_texts.append("References of 00000064 (00000064)")
        lst_texts.append("Pointers of 00000064 (00000064)")
        lst_texts.append("Name: Blubb")
        lst_texts.append("Selected reference leads to 00000068 (00000068)")

        for i in range(0,len(lst_texts)):
            tli = self.properties_window.tvProps.topLevelItem(i)
            assert isinstance(tli,QtWidgets.QTreeWidgetItem)
            if i == 0:
                child = tli.child(0)
                assert isinstance(child,QtWidgets.QTreeWidgetItem)
                self.assertEqual(child.text(0),"00123456")
            if i == 1:
                child = tli.child(0)
                assert isinstance(child,QtWidgets.QTreeWidgetItem)
                self.assertEqual(child.text(0),"+00000004 to 00000083 (00000083)")
            self.assertEqual(tli.text(0),lst_texts[i])

        tli = self.properties_window.tvProps.topLevelItem(2)
        assert isinstance(tli,QtWidgets.QTreeWidgetItem)
        self.properties_window.item_click(tli)
        tli = self.properties_window.tvProps.topLevelItem(2)
        assert isinstance(tli,QtWidgets.QTreeWidgetItem)
        self.assertEqual(tli.text(0),"Name: Test123")


if __name__ == "__main__":
    unittest.main()
