import sys
import os
from ReferenceSearcher import *
from MarkedRegions import *
from PyQt5.QtCore import *
import unittest

class IdxMock(QModelIndex):
    def __init__(self,row,col):
        QModelIndex.__init__(self)
        self.row=row
        self.col=col

class ModelMock:
    def createIndex(self,row,col):
        return IdxMock(row,col)

class MarkableGridMock:
    def __init__(self):
        self.width=32
        self.model=ModelMock()

class ReferenceSearcherTest(unittest.TestCase):
    def testReferenceSearcher(self):
        Globals.r_searcher = ReferenceSearcher(None)
        Globals.hex_grid = MarkableGridMock()
        regions = []
        all_references = ReferenceList()

        all_references.append(Reference(60))

        r = MarkedRegion(50, 100)
        regions.append(r)
        Globals.r_searcher.search_all_pointers(regions, all_references)

        assert len(r.pointers) > 0, "PointerList of region is empty!"

if __name__ == "__main__":
    unittest.main()