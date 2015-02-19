from PyQt5           import QtCore,QtGui,QtWidgets,uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui     import QCursor
from PyQt5.QtCore    import Qt
from struct          import *
import base64

SearchResultsUI = uic.loadUiType("searchResults.ui")[0]

class SearchResults(QtWidgets.QMainWindow,SearchResultsUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent   = parent
        self.prevList = []
        self.setupUi(self)

    def show(self):
        self.cancelSearch = False
        self.pos          = 0
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.listNext()
        QApplication.restoreOverrideCursor()
        super().show()
        self.setFocus()

    def selectionChanged(self,txt):
        if txt=="" or txt==None:
            return
        print("selectionChanged %s" % txt)
        pos = int(txt, 16)
        self.parent.callback(pos)

    def reject(self):
        self.cancelSearch = True
        super().hide()

    def next(self):
        print("next")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.listNext()
        QApplication.restoreOverrideCursor()

    def prev(self):
        print("prev")
        self.pos = self.prevList[len(self.prevList)-1]
        self.prevList.remove(len(self.prevList)-1)
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.listNext()
        QApplication.restoreOverrideCursor()
    
    def listNext(self):
        i = 0;
        if len(self.prevList) > 0:
            self.btnPrev.setEnabled(True)
        else:
            self.btnPrev.setEnabled(False)
        
        if self.pos == -1:
            return
        self.prevList.append(self.pos)
        while((i<100) and self.pos!=-1 and not self.cancelSearch):
            i        += 1
            self.pos  = self.parent.searchNext()
            if self.pos != -1:
                self.listSearchResults.addItem("%08x" % self.pos)
        if i == 100:
            self.btnNext.setEnabled(True)
        else:
            self.btnNext.setEnabled(False)
