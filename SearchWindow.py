from PyQt5 import QtCore, QtGui, QtWidgets, uic
from struct import *
from SearchResults import *
from CachedReader import *
import base64
import binascii
import Globals

SearchUI = uic.loadUiType("search.ui")[0]


class SearchWindow(QtWidgets.QMainWindow, SearchUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)
        self.file = None
        self.search_data = None
        self.insensitive = False
        self.search_results = SearchResults(self)

    def show(self, file, size, callback ,show_window = True):
        self.pos = 0
        self.size = size
        self.file = CachedReader(file)
        self.callback = callback
        Globals.main_window.action_Search_Next.setEnabled(True)
        self.txtSearch.setFocus()
        if show_window:
            super().show()

    def prepare_search(self):
        if self.cbType.currentText() == "hex":
            self.insensitive = False
            txt = self.txtSearch.text().replace(" ", "")
            try:
                self.search_data = base64.b16decode(txt.upper())
            except(binascii.Error):
                self.cbType.setCurrentIndex(1)
        if self.cbType.currentText() == "text":
            self.insensitive = True
            self.search_data = self.txtSearch.text()

    def accept(self):
        dbg("accept")
        self.prepare_search()
        pos = self.search_next()
        if pos <= 0:
            super().hide()
            return
        self.callback(pos)
        super().hide()

    def reject(self):
        dbg("reject")
        self.hide()

    def search_all(self):
        self.prepare_search()
        self.search_results.show()
        self.hide()

    def search_next(self):
        dbg("searchNext")
        if self.pos == -1:
            return
        self.file.seek(self.pos)
        while self.pos < self.size:
            buf = self.file.read(self.file.cache_size)
            if len(buf) == 0:
                self.pos = -1
                break
            try:
                if self.insensitive:
                    p = bytes(buf).lower().index(bytes(self.search_data, "UTF-8").lower())
                else:
                    p = bytes(buf).index(bytes(self.search_data, "UTF-8"))
                brange = bytes(buf[p:p + len(self.search_data)]).lower()
                # if brange == bytes(self.searchData,"UTF-8").lower():
                self.pos += p
                dbg("searchNext text: %s (searched %s, found at idx %d, pos: %08x)" % (
                brange, self.search_data, p, self.pos))
                break;
                #else:
                #    dbg("not equal ... %s(%d) %s(%d)" % (brange,len(brange),self.searchData,len(self.searchData)))
                #    self.pos += p + 1
            except(ValueError):
                self.pos += self.file.cache_size
        if self.pos == -1:
            return -1
        pos = self.pos
        self.pos += len(self.search_data)
        if (self.pos >= self.size):
            self.pos = -1
            return -1
        dbg("search_next result:%08x" % self.pos)
        return pos
