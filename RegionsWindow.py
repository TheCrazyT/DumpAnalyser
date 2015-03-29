from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals
from MarkedRegions import *

RegionsUI = uic.loadUiType("regions.ui")[0]


class RegionsWindow(QtWidgets.QMainWindow, RegionsUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def regionSelected(self, widget):
        if widget != None:
            self.parent.set_pos(widget.pos)

    def show(self):
        self.lstRegions.clear()
        for r in Globals.hex_grid.regions.region_list:
            name = None
            for p in r.properties:
                if type(p) is NullString:
                    start_pos = p.start_pos
                    end_pos = p.end_pos
                    try:
                        if end_pos == -1:
                            buf = Globals.main_window.read_txt(start_pos, 1024)
                            end_pos = start_pos + buf.index(".")
                        name = Globals.main_window.read_txt(start_pos, end_pos - start_pos)
                        break
                    except:
                        continue
            if name != None:
                item = QtWidgets.QListWidgetItem("%08x [%s]" % (r.start_pos, name))
                item.pos = r.start_pos
                self.lstRegions.addItem(item)
            else:
                item = QtWidgets.QListWidgetItem("%08x" % (r.start_pos))
                item.pos = r.start_pos
                self.lstRegions.addItem(item)
        super().show()
        self.activateWindow()
