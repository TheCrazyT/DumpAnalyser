import sys
import os
import struct
from ReferenceSearcher import *
from MarkedRegions import *
from PyQt5.QtCore import *
import unittest

class CachedReaderMock():
    def __init__(self):
        self.cache_size = 1024
        self._buf = []
        self._modify_list = {}
        self._pos = 0
    def read(self,size):
        self._buf = []
        for i in range(0,size):
            if self._pos+i in self._modify_list:
                self._buf.append(self._modify_list[self._pos+i])
            else:
                self._buf.append(i%255)
        self._pos += size
        return bytes(self._buf)
    def modify(self,pos,value):
        data = struct.pack("I",value)
        self._modify_list[pos] = data[0]
        self._modify_list[pos+1] = data[1]
        self._modify_list[pos+2] = data[2]
        self._modify_list[pos+3] = data[3]
    def seek(self,pos):
        self._pos = pos

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

class MainWindowMock:
    def __init__(self):
        self.rva_list = [(0,0,1000)]

    def read_pointer(self,pos):
        assert pos == 0x68
        dbg("read_pointer %08x" % pos)
        return struct.pack("I",0x83)

class ReferenceSearcherTest(unittest.TestCase):
    def setUp(self):
        Globals.SLEEP_BETWEEN_REGION_READ = 0
        Globals.SLEEP_BETWEEN_REGION_SCAN = 0
        Globals.SLEEP_BETWEEN_REGIONS = 0
        Globals.SLEEP_BETWEEN_PAGE_VALUE = 0
        Globals.r_searcher = ReferenceSearcher(None)
        Globals.main_window = MainWindowMock()
        Globals.hex_grid = MarkableGridMock()
        Globals.DEBUG = True

    def test_search_all_pointers(self):
        dbg("test_search_all_pointers")
        regions = []
        all_references = ReferenceList()

        all_references.append(Reference(60))

        r = MarkedRegion(50, 100)
        regions.append(r)
        Globals.r_searcher.search_all_pointers(regions, all_references)

        assert len(r.pointers) > 0, "PointerList of region is empty!"

    def test_index_pages(self):
        dbg("test_index_pages")
        r_searcher = Globals.r_searcher
        assert isinstance(r_searcher,ReferenceSearcher)
        r_searcher.set_size(1024*10)
        r_searcher.set_file(CachedReaderMock())
        r_searcher.index_pages()
        assert r_searcher.is_value_in_page(0x1112,0)

    def test_search_all(self):
        dbg("test_search_all")
        r_searcher = Globals.r_searcher
        assert isinstance(r_searcher,ReferenceSearcher)
        search_regions = []
        pos = 1024*1+100
        r = MarkedRegion(pos,10)
        file = CachedReaderMock()
        search_regions.append(r)
        r_searcher.set_size(1024*10)
        r_searcher.set_file(file)
        file.modify(1024+10,pos)
        r_searcher.index_pages()
        r_searcher.search_all(search_regions)
        assert len(r.references)>0

    def test_guess_regions(self):
        file = CachedReaderMock()
        dbg("guess_regions")
        r_searcher = Globals.r_searcher
        assert isinstance(r_searcher,ReferenceSearcher)

        r_searcher.set_size(1024*10)
        r_searcher.set_file(file)
        file.modify(3,2000-20)
        file.modify(1024+30,4000-20)
        file.modify(1024*2+30,4000-21)
        r_searcher.index_pages()
        references = ReferenceList()
        r1 = Reference(2000)
        references.append(r1)
        r2 = Reference(4000)
        references.append(r2)
        r_searcher.guess_regions(references)
        ref1 = r_searcher.get_ref(r1)
        ref2 = r_searcher.get_ref(r2)
        assert(ref1.get_fully_scanned())
        assert(len(ref1.get_guessed_regions())==1)
        assert(len(ref2.get_guessed_regions())==2)

if __name__ == "__main__":
    unittest.main()