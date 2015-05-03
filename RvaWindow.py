from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals
from   Globals import *

RvaMapUI = uic.loadUiType("rva_map.ui")[0]


class RvaWindow(QtWidgets.QMainWindow, RvaMapUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def show(self):
        self.lstRva.clear()
        for x in Globals.main_window.get_rva_list():
            (rva, vaddr, size) = x
            self.lstRva.addItem("%08x,%08x,%08x" % (rva, vaddr, size))
        super().show()
        self.setFocus()

    def accept(self):
        dbg("accept")
        for line in self.rvaInput.toPlainText().split("\n"):
            (rva, vaddr, size) = line.split(",")
            Globals.main_window.get_rva_list().append((int(rva, 16), int(vaddr, 16), int(size, 16)))
        self.hide()

    def reject(self):
        dbg("reject")
        self.hide()
