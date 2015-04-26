from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from struct import *
import base64

SearchResultsUI = uic.loadUiType("searchResults.ui")[0]


class SearchResults(QtWidgets.QMainWindow, SearchResultsUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.prev_list = []
        self.setupUi(self)

    def show(self):
        self.cancel_search = False
        self.pos = 0
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.list_next()
        QApplication.restoreOverrideCursor()
        super().show()
        self.setFocus()

    def selectionChanged(self, txt):
        if txt == "" or txt is None:
            return
        print("selectionChanged %s" % txt)
        pos = int(txt, 16)
        self.parent.callback(pos)

    def reject(self):
        self.cancel_search = True
        super().hide()

    def next(self):
        print("next")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.list_next()
        QApplication.restoreOverrideCursor()

    def prev(self):
        print("prev")
        self.pos = self.prev_list[len(self.prev_list) - 1]
        self.prev_list.remove(len(self.prev_list) - 1)
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.listSearchResults.clear()
        self.list_next()
        QApplication.restoreOverrideCursor()

    def list_next(self):
        i = 0;
        if len(self.prev_list) > 0:
            self.btnPrev.setEnabled(True)
        else:
            self.btnPrev.setEnabled(False)

        if self.pos == -1:
            return
        self.prev_list.append(self.pos)
        while ((i < 100) and self.pos != -1 and not self.cancel_search):
            i += 1
            self.pos = self.parent.search_next()
            if self.pos != -1:
                self.listSearchResults.addItem("%08x" % self.pos)
        if i == 100:
            self.btnNext.setEnabled(True)
        else:
            self.btnNext.setEnabled(False)
