from PyQt5         import QtCore,QtGui,QtWidgets,uic
from struct        import *
from SearchResults import *
from CachedReader  import *
import base64
import binascii

SearchUI = uic.loadUiType("search.ui")[0]

class SearchWindow(QtWidgets.QMainWindow,SearchUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)
        self.file          = None
        self.searchData    = None
        self.insensitive   = False
        self.searchResults = SearchResults(self)

    def show(self,file,size,callback):
        self.pos      = 0
        self.size     = size
        self.file     = CachedReader(file)
        self.callback = callback
        self.parent.action_Search_Next.setEnabled(True)
        super().show()
        self.txtSearch.setFocus()

    def prepareSearch(self):
        if self.cbType.currentText() == "hex":
            self.insensitive = False
            txt = self.txtSearch.text().replace(" ","")
            try:
                self.searchData = base64.b16decode(txt.upper())
            except(binascii.Error):
                self.cbType.setCurrentIndex(1)
        if self.cbType.currentText() == "text":
            self.insensitive = True
            self.searchData  = self.txtSearch.text()
        
    def accept(self):
        dbg("accept")
        self.prepareSearch()
        pos = self.searchNext()
        if pos <= 0:
            super().hide()
            return
        self.callback(pos)
        super().hide()

    def reject(self):
        dbg("reject")
        self.hide()

    def searchAll(self):
        self.prepareSearch()
        self.searchResults.show()
        self.hide()

    def searchNext(self):
        dbg("searchNext")
        if self.pos == -1:
            return
        self.file.seek(self.pos)
        while self.pos<self.size:
            buf        = self.file.read(self.file.cacheSize)
            if len(buf) == 0:
                self.pos = -1
                break
            try:
                if self.insensitive:
                    p     = bytes(buf).lower().index(bytes(self.searchData,"UTF-8").lower())
                else:
                    p     = bytes(buf).index(bytes(self.searchData,"UTF-8"))
                brange = bytes(buf[p:p+len(self.searchData)]).lower()
                #if brange == bytes(self.searchData,"UTF-8").lower():
                self.pos += p
                dbg("searchNext text: %s (searched %s, found at idx %d, pos: %08x)" % (brange,self.searchData,p,self.pos))
                break;
                #else:
                #    dbg("not equal ... %s(%d) %s(%d)" % (brange,len(brange),self.searchData,len(self.searchData)))
                #    self.pos += p + 1
            except(ValueError):
                self.pos += self.file.cacheSize
        if self.pos == -1:
            return -1
        pos       = self.pos
        self.pos += len(self.searchData)
        if(self.pos >= self.size):
            self.pos = -1
            return -1
        dbg("searchNext result:%08x" % self.pos)
        return pos
