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
class RegionListTest(unittest.TestCase):
    def setUp(self):
        Globals.DEBUG = True
        Globals.hex_grid = MarkableGridMock()

    def testRegionList(self):
        region = MarkedRegion(0x1234,10)
        rlist = RegionList()
        rlist.append(region)
        find_within_list = rlist.find_within(1,0x2000)
        self.assertEqual(len(find_within_list),1)
        find_containing_list = rlist.find_region_containing(0x1236,0x1238)
        self.assertEqual(len(find_containing_list),1)


if __name__ == "__main__":
    unittest.main()