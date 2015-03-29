import sys
import os
import Globals
from SearchWindow import *
import unittest
import struct

class ActionMock:
    def setEnabled(self,value):
        pass

class MainWindowMock:
    def __init__(self,size=500000000):
        self.size = size
        self.file_size = size
        self.rva_list = []
        self.action_Search_Next = ActionMock()

    def readHex(self, pos):
        return "00"

    def readTxt(self, pos, l):
        return "?" * l

class FileMock:
    def __init__(self):
        self.locker = None
    def tell(self):
        pass
    def seek(self,pos):
        pass
    def read(self,len):
        return bytes("%s%s%s" % ("x"*5,"test","x"*8),"UTF-8")

class SearchWindowTest(unittest.TestCase):
    def testSearchWindow(self):
        app = QtWidgets.QApplication(sys.argv)
        Globals.main_window = MainWindowMock(200)
        Globals.search_window = SearchWindow()
        Globals.search_window.txtSearch.setText("test")
        file = FileMock()
        size = 10
        callback = self.search_callback
        Globals.search_window.show(file, size, callback ,False)
        Globals.search_window.search_all()
        assert Globals.search_window.search_results.listSearchResults.count() == 1

    def search_callback(self):
        pass

if __name__ == "__main__":
    unittest.main()