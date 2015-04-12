import unittest
import Globals
from MarkedRegions import *
from PyQt5.QtCore import *

class MarkableGridMock:
    def __init__(self):
        self.width = 32
        self.model = ModelMock()
class ModelMock(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
    def createIndex(self,row,col):
        dbg("createIndex(%d,%d)" % (row,col))
        return super().createIndex(row,col)
class ReferenceListTest(unittest.TestCase):
    def testReferenceList(self):
        Globals.DEBUG = True
        Globals.hex_grid = MarkableGridMock()
        reference_list = ReferenceList()
        r = Reference(0x123456)
        reference_list.append(r)
        dbg("Reference list count:%d" % len(reference_list))
        for r in reference_list:
            dbg("Reference:%s" % r)
        assert(not(0x123455 in reference_list))
        assert(0x123456 in reference_list)
        assert(0x123457 in reference_list)
        assert(0x123458 in reference_list)
        assert(0x123459 in reference_list)
        assert(not(0x12345A in reference_list))
        assert(not(0x12345B in reference_list))
        assert(not(0x12345C in reference_list))

if __name__ == "__main__":
    unittest.main()