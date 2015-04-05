import sys
import os
import unittest
from PropertiesWindow import *
from MarkedRegions import *
from MarkableGrid import *
from ReferenceSearcher import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class SelectedCells(list):
    def __contains__(self, c):
        for cell in self:
            if (cell[0] == c[0]) and (cell[1] == c[1]):
                return True
        return False


class ActionRefMock:
    def isChecked(self):
        return False


class MainWindowMock:
    def __init__(self,size=500000000):
        self.size = size
        self.file_size = size
        self.rva_list = []
        self.action_References = ActionRefMock()

    def readHex(self, pos):
        return "00"

    def readTxt(self, pos, l):
        return "?" * l


class ToolMenuMock:
    def enableRegion(self):
        print("enableRegion")

    def enableRegionButtons(self):
        print("enableRegionButtons")


def check(cells, grid, width):
    cellsChecked = SelectedCells()
    cellCnt = 0
    for i in grid.selection_model.selectedIndexes():
        if (i.column(), i.row()) not in cells:
            raise Exception(
                "Cell %d,%d (%d) should not be selected!" % (i.column(), i.row(), i.row() * width + i.column()))
        else:
            cellCnt += 1
            cellsChecked.append((i.column(), i.row()))
    if cellCnt != len(cells):
        print("cellsChecked: %s" % cellsChecked)
        raise Exception("Not all needed cells selected! (%d != %d)" % (cellCnt, len(cells)))


class MarkableGridTest(unittest.TestCase):

    def testReferences(self):
        app = QtWidgets.QApplication(sys.argv)
        Globals.main_window = MainWindowMock(200)
        Globals.tool_menu = ToolMenuMock()
        Globals.DEBUG = True
        width = 32
        height = 32
        grid = MarkableGrid(Globals.main_window, width, height)
        reference = Reference(20)
        grid.all_references.append(reference)
        grid.update()

    def testRegion(self):
        app = QtWidgets.QApplication(sys.argv)
        Globals.main_window = MainWindowMock(200)
        Globals.tool_menu = ToolMenuMock()
        Globals.DEBUG = True
        width = 32
        height = 32
        grid = MarkableGrid(Globals.main_window, width, height)
        region = MarkedRegion(2,5)
        grid.regions.append(region)
        grid.update()

    def testGrid(self):
        app = QtWidgets.QApplication(sys.argv)
        Globals.main_window = MainWindowMock()
        Globals.tool_menu = ToolMenuMock()
        Globals.DEBUG = True
        width = 32
        height = 32
        grid = MarkableGrid(Globals.main_window, width, height)
        #grid.show()
        grid.update()

        cells = SelectedCells()
        cells.append((width, 0))
        grid.temp_select(width - 1, 1)

        print("Check 1")
        check(cells, grid,width )

        cells = SelectedCells()
        cells.append((width, 0))
        cells.append((1, 1))
        cells.append((0, 1))
        grid.temp_select(width - 1, 2)

        print("Check 2")
        check(cells, grid, width)

        cells = SelectedCells()
        grid.temp_select(8 * width + 12, width)
        for i in range(8 * width + 12, 8 * width + 12 + width):
            x = i % width
            y = int((i - x) / width)
            x += 1
            cells.append((x, y))
            print("select %d,%d" % (x, y))
            if x == 1:
                if (0, y) not in cells:
                    cells.append((0, y))
                    print("select %d,%d" % (0, y))

        print("Check 3")
        check(cells, grid, width)

        cells = SelectedCells()
        grid.temp_select(442609052, 442609066 - 442609052 + 1)
        for i in range(442609052, 442609067):
            x = i % width
            y = int((i - x) / width)
            x += 1
            cells.append((x, y))
            print("select %d,%d" % (x, y))
            if x == 1:
                if (0, y) not in cells:
                    cells.append((0, y))
                    print("select %d,%d" % (0, y))

        idx = grid.model.index(cells[0][1], 0, QtCore.QModelIndex())
        grid.scrollTo(idx)
        print("Check 4")
        check(cells, grid, width)

if __name__ == "__main__":
    unittest.main()