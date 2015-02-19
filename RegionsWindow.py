from PyQt5         import QtCore,QtGui,QtWidgets,uic
import Globals

RegionsUI = uic.loadUiType("regions.ui")[0]

class RegionsWindow(QtWidgets.QMainWindow,RegionsUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def regionSelected(self,widget):
        self.parent.setPos(int(widget.text(),16))
        
    def show(self):
        self.lstRegions.clear()
        for r in Globals.hexGrid.regions.regionList:
            self.lstRegions.addItem("%08x" % r.startPos)
        super().show()
        self.activateWindow()
