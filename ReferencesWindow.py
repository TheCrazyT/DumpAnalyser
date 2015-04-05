from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals

RegionsUI = uic.loadUiType("references.ui")[0]


class ReferencesWindow(QtWidgets.QMainWindow, RegionsUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def referenceSelected(self, widget):
        if widget != None:
            Globals.main_window.set_pos(int(widget.text(), 16))

    def show(self):
        self.lstRefs.clear()
        for r in Globals.hex_grid.all_references:
            self.lstRefs.addItem("%08x" % r.addr)
        super().show()
        self.activateWindow()
