import tempfile
import os
import db
import Globals
import unittest

from MarkedRegions import *
from ReferenceSearcher import ReferenceWrapper
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *

class ModelMock(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

class MarkableGridMock:
    def __init__(self):
        self.width = 32
        self.model = ModelMock()

class ReferenceSearcherMock:
    def get_ref(self,o):
        return ReferenceWrapper(o)
    def reset_ref_map(self):
        pass
    def get_indexed_pages(self):
        indexed_pages = []
        page = set()
        page.add(0x1234)
        indexed_pages.append(page)
        return indexed_pages
    def set_indexed_pages(self,indexed_pages):
        pass

class dbTest(unittest.TestCase):
    def setUp(self):
        self.file = tempfile.mktemp()
        Globals.r_searcher = ReferenceSearcherMock()
        Globals.hex_grid = MarkableGridMock()
        Globals.DEBUG = True
        db.connect(self.file)
        db.create_regions_tbl()
        db.create_regions_ref_tbl()
        db.create_indexed_pages()
    def tearDown(self):
        db.close()
        os.remove(self.file)
    def testRegion(self):
        r = MarkedRegion(0,10,100)
        r.references.append(Reference(0x123456))
        r.set_color("red")
        r.set_name("test")
        db.save_region(r)
        db.save_indexed_pages()
        regions = db.load_regions()
        db.load_indexed_pages()
        assert(len(regions)==1)
        r = regions[0]
        assert(r.get_color_value() == "red")
        assert(r.get_name() == "test")

if __name__ == "__main__":
    unittest.main()