from PyQt5         import QtCore,QtGui,QtWidgets,uic
import Globals
from MarkedRegions import *

RegionsUI = uic.loadUiType("regions.ui")[0]

class RegionsWindow(QtWidgets.QMainWindow,RegionsUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def regionSelected(self,widget):
        if widget != None:
            self.parent.setPos(widget.pos)
        
    def show(self):
        self.lstRegions.clear()
        for r in Globals.hexGrid.regions.regionList:
            name = None
            for p in r.properties:
                if type(p) is NullString:
                    startPos = p.startPos
                    endPos   = p.endPos
                    try:
                        if endPos==-1:
                            buf = Globals.mainWindow.readTxt(startPos,1024)
                            endPos = startPos + buf.index(".")
                        name     = Globals.mainWindow.readTxt(startPos,endPos-startPos)
                        break
                    except:
                        continue
            if name!=None:
                item     = QtWidgets.QListWidgetItem("%08x [%s]" % (r.startPos,name))
                item.pos = r.startPos
                self.lstRegions.addItem(item)
            else:
                item     = QtWidgets.QListWidgetItem("%08x" % (r.startPos))
                item.pos = r.startPos
                self.lstRegions.addItem(item)
        super().show()
        self.activateWindow()
