import sys
import os
import unittest
from PyQt5.uic.Compiler.qtproxies import QtWidgets
from PropertiesWindow import *
from MarkedRegions import *
from MarkableGrid import *
from ReferenceSearcher import *
from Globals import dbg
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class SelectedCells(list):
    def __contains__(self, c):
        for cell in self:
            if (cell[0] == c[0]) and (cell[1] == c[1]):
                return True
        return False


class ActionRefMock:
    def isChecked(self):
        return True

class MainWindowMock:
    def __init__(self,size=500000000):
        self.size = size
        self.file_size = size
        self.rva_list = []
        self.pos = 0
        self.action_References = ActionRefMock()

    def read_hex(self, pos):
        return "00"

    def read_txt(self, pos, l):
        return "?" * l

class ReferenceSearcherMock:
    def invalidate_pointer_search(self,regions):
        pass
    def calculate_pointer_pos_rva(self,pos):
        return pos

class ToolMenuMock:
    def enableRegion(self):
        dbg("enableRegion")

    def enableRegionButtons(self):
        dbg("enableRegionButtons")


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
        dbg("cellsChecked: %s" % cellsChecked)
        raise Exception("Not all needed cells selected! (%d != %d)" % (cellCnt, len(cells)))


class MarkableGridTest(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication(sys.argv)
        Globals.main_window = MainWindowMock(200)
        Globals.tool_menu = ToolMenuMock()
        Globals.DEBUG = True
        Globals.r_searcher = ReferenceSearcherMock()
        self.width = 32
        self.height = 32

    def testReferences(self):
        grid = MarkableGrid(Globals.main_window, self.width, self.height)
        grid.update()
        reference = Reference(20)
        grid.all_references.append(reference)
        grid.update()

    def testRegion(self):
        grid = MarkableGrid(Globals.main_window, self.width, self.height)
        grid.update()
        region = MarkedRegion(2,5)
        grid.regions.append(region)
        grid.update()

    def testGrid(self):
        Globals.main_window = MainWindowMock(442609052+100)
        grid = MarkableGrid(Globals.main_window, self.width, self.height)
        #grid.show()
        grid.update()

        cells = SelectedCells()
        cells.append((self.width, 0))
        grid.temp_select(self.width - 1, 1)

        dbg("Check 1")
        check(cells, grid,self.width )

        cells = SelectedCells()
        cells.append((self.width, 0))
        cells.append((1, 1))
        cells.append((0, 1))
        grid.temp_select(self.width - 1, 2)

        dbg("Check 2")
        check(cells, grid, self.width)

        cells = SelectedCells()
        grid.temp_select(8 * self.width + 12, self.width)
        for i in range(8 * self.width + 12, 8 * self.width + 12 + self.width):
            x = i % self.width
            y = int((i - x) / self.width)
            x += 1
            cells.append((x, y))
            dbg("select %d,%d" % (x, y))
            if x == 1:
                if (0, y) not in cells:
                    cells.append((0, y))
                    dbg("select %d,%d" % (0, y))

        print("Check 3")
        check(cells, grid, self.width)

        cells = SelectedCells()
        grid.temp_select(442609052, 442609066 - 442609052 + 1)
        for i in range(442609052, 442609067):
            x = i % self.width
            y = int((i - x) / self.width)
            x += 1
            cells.append((x, y))
            dbg("select %d,%d" % (x, y))
            if x == 1:
                if (0, y) not in cells:
                    cells.append((0, y))
                    dbg("select %d,%d" % (0, y))

        idx = grid.model.index(cells[0][1], 0, QtCore.QModelIndex())
        grid.scrollTo(idx)
        dbg("Check 4")
        check(cells, grid, self.width)

        result = grid.detect_region_action(40,50)
        self.assertEqual(result[0],MarkableGrid.NEW_REGION)
        grid.temp_select(40,10)
        grid.store_region()
        result = grid.detect_region_action(30,50)
        self.assertEqual(result[0],MarkableGrid.RESIZE_REGION)

        for i in range(40,49):
            r, reference, show_refs = grid.find_region_at(i)
            self.assertIsInstance(r,list)
            self.assertEqual(len(r),1)
            self.assertEqual(r[0].start_pos ,40)
            self.assertEqual(r[0].end_pos ,49)

        r, reference, show_refs = grid.find_region_at(50)
        self.assertIsInstance(r,list)
        self.assertEqual(len(r),0)

        r, reference, show_refs = grid.find_region_at(39)
        self.assertIsInstance(r,list)
        self.assertEqual(len(r),0)

        grid.all_references.append(Reference(64))
        idx = grid.model.index(0, 0, QtCore.QModelIndex())
        grid.scrollTo(idx)
        grid.update_view()
        assert len(grid.view_regions)!=0
        dbg("Pos: %d" % Globals.main_window.pos)

        ref_green = []
        ref_green.append((0,2))
        ref_green.append((1,2))
        ref_green.append((2,2))
        ref_green.append((3,2))
        for rl in grid.view_regions:
            assert len(rl)!=0
            found = False
            for r in rl:
                (item, color) = r
                self.assertIsInstance(color,QtGui.QColor)
                if (item.x,item.y) in ref_green:
                    self.assertEqual(color.green(),0xFF)
                    self.assertEqual(color.red(),0)
                    self.assertEqual(color.blue(),0)
                    found = True
                else:
                    assert not((color.red() == 0)and(color.green() == 0xFF)and(color.blue() == 0)),"invalid colored cell at %d,%d (%02x,%02x,%02x)" % (item.x,item.y,color.red(),color.green(),color.blue())
            assert found,"Reference was not found"

        r, reference, show_refs = grid.find_region_at(63)
        assert not show_refs
        assert reference is None
        r, reference, show_refs = grid.find_region_at(64)
        assert show_refs
        assert reference != None
        r, reference, show_refs = grid.find_region_at(65)
        assert show_refs
        assert reference != None
        r, reference, show_refs = grid.find_region_at(66)
        assert show_refs
        assert reference != None
        r, reference, show_refs = grid.find_region_at(67)
        assert show_refs
        assert reference != None
        r, reference, show_refs = grid.find_region_at(68)
        assert not show_refs
        assert reference is None



if __name__ == "__main__":
    unittest.main()