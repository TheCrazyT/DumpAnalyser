import sys
import os
from PropertiesWindow  import *
from MarkedRegions     import *
from MarkableGrid      import *
from ReferenceSearcher import *
from PyQt5             import QtCore, QtGui, QtWidgets, uic

class SelectedCells(list):
    def __contains__(self,c):
        for cell in self:
            if (cell[0] == c[0])and(cell[1] == c[1]):
                return True
        return False

class MainWindowMock:
    def __init__(self):
        self.size        = 12000
        self.fileSize    = 12000
        self.rvaList     = []

class ToolMenuMock:
    def __init__(self):
        print("toolMenu")
    def enableRegion(self):
        print("enableRegion")
    def enableRegionButtons(self):
        print("enableRegionButtons")

if __name__ == "__main__":
    app                = QtWidgets.QApplication(sys.argv)
    Globals.mainWindow = MainWindowMock()
    Globals.toolMenu   = ToolMenuMock()
    width              = 32
    height             = 32
    grid               = MarkableGrid(Globals.mainWindow,width,height)
    grid.show()
    grid.update()

    cells              = SelectedCells()
    cellsChecked       = SelectedCells()
    cells.append((0,width))
    cells.append((1,1))
    cells.append((1,0))
    grid.temp_select(width-1,1)

    cellCnt            = 0
    for i in grid.selectionModel.selectedIndexes():
        if (i.row(),i.column()) not in cells:
            raise Exception("Cell %d,%d should not be selected!" % (i.row(),i.column()))
        else:
            cellCnt += 1
            cellsChecked.append((i.row(),i.column()))
    if cellCnt != len(cells):
        print("cellsChecked: %s" % cellsChecked)
        raise Exception("Not all needed cells selected! (%d != %d)" % (cellCnt,len(cells)))
    
    sys.exit(app.exec_())
