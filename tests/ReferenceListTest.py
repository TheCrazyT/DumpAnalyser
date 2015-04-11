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
        rlist = ReferenceList()
        r = Reference(0x123456)
        rlist.append(r)
        dbg("Reference list count:%d" % len(rlist))
        for r in rlist:
            dbg("Reference:%s" % r)
        assert(0x123456 in rlist)
        assert(0x123457 in rlist)
        assert(0x123458 in rlist)
        assert(0x123459 in rlist)
        assert(not(0x12345A in rlist))
        assert(not(0x12345B in rlist))
        assert(not(0x12345C in rlist))

if __name__ == "__main__":
    unittest.main()