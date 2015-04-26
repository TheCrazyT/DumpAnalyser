from PyQt5 import QtCore, QtGui, QtWidgets
from MarkedRegions import *
import Globals
from Globals import *

class CustomSelection(QtCore.QItemSelection):
    def __init__(self, first_idx, last_idx):
        QtCore.QItemSelection.__init__(self, first_idx, last_idx)
        width = Globals.hex_grid.width
        height = Globals.hex_grid.height
        self.first_idx = first_idx.row() * (width + 2) + first_idx.column()
        self.last_idx = last_idx.row() * (width + 2) + last_idx.column()
        self.idx_list = None

    def indexes(self):
        width = Globals.hex_grid.width
        row = Globals.hex_grid.row
        if self.idx_list is None:
            self.idx_list = []
            for i in range(self.first_idx, self.last_idx):
                column = i % (width + 2)
                row = int((i - column) / (width + 2))
                self.idx_list.append(Globals.hex_grid.model.createIndex(row, column))
        return self.idx_list


class MySelectionModel(QtCore.QItemSelectionModel):
    def __init__(self, model):
        QtCore.QItemSelectionModel.__init__(self, model)
        self.model = model

    def select(self, i, flags):
        width = Globals.hex_grid.width
        height = Globals.hex_grid.height
        if (type(i) is CustomSelection) or (type(i) is QtCore.QItemSelection):
            if (flags & QtCore.QItemSelectionModel.Select):
                Globals.tool_menu.enableRegion()
                Globals.tool_menu.enableRegionButtons()
                max_idx = None
                min_idx = None

                cIdx = self.currentIndex()
                if (type(i) is CustomSelection):
                    min_idx = i.first_idx
                    max_idx = i.last_idx
                elif (type(i) is QtCore.QItemSelection):
                    maxR = None
                    minR = None
                    for k in i.indexes():
                        if (maxR is None) or (k.row() > maxR):
                            maxR = k.row()
                        if (minR is None) or (k.row() < minR):
                            minR = k.row()

                    for k in i.indexes():
                        idx = k.row() * (width + 2) + k.column()
                        if k.row() == minR:
                            if (min_idx is None) or (idx > min_idx):
                                min_idx = k.row() * (width + 2) + k.column()
                        if k.row() == maxR:
                            if (max_idx is None) or (idx < max_idx):
                                max_idx = k.row() * (width + 2) + k.column()
                    if min_idx is None:
                        return
                # max_idx = cIdx.row()*width+cIdx.column()

                col1 = min_idx % (width + 2)
                col2 = max_idx % (width + 2)
                row1 = int((min_idx - col1) / (width + 2))
                row2 = int((max_idx - col2) / (width + 2))
                if (not type(i) is CustomSelection):
                    if cIdx.column() != -1:
                        if cIdx.column() != col2:
                            col1 = col2
                            col2 = cIdx.column()
                if row1 != row2:
                    i.clear()
                dbg("cIdx.column(): %d,min_idx: %d, max_idx: %d, row1: %d, row2: %d, col1: %d, col2: %d" % (
                cIdx.column(), min_idx, max_idx, row1, row2, col1, col2))
                if row1 + 2 <= row2:
                    idx1 = self.model.createIndex(row1 + 1, 0)
                    idx2 = self.model.createIndex(row2 - 1, width)
                    sr = QtCore.QItemSelectionRange(idx1, idx2)
                    i.append(sr)
                if row1 < row2:
                    idx1 = self.model.createIndex(row1, col1)
                    idx2 = self.model.createIndex(row1, width)
                    sr = QtCore.QItemSelectionRange(idx1, idx2)
                    i.append(sr)
                    idx1 = self.model.createIndex(row2, 0)
                    idx2 = self.model.createIndex(row2, col2)
                    sr = QtCore.QItemSelectionRange(idx1, idx2)
                    i.append(sr)
        super().select(i, flags)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)

    def supportedDragActions(self):
        return QtCore.Qt.MoveAction

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def rowCount(self, parent):
        if Globals.main_window.size is None:
            return 0
        if Globals.hex_grid.width == 0:
            return 0
        return int(Globals.main_window.file_size / Globals.hex_grid.width)

    def columnCount(self, parent):
        return Globals.hex_grid.width + 2

    def data(self, index, role):
        if role == QtCore.Qt.BackgroundRole:
            if index.column() != 0:
                if index.column() != Globals.hex_grid.width + 1:
                    if Globals.hex_grid.text != None:
                        rect = Globals.hex_grid.viewport().rect()
                        topRow = Globals.hex_grid.indexAt(rect.topLeft()).row()
                        x = index.column() - 1
                        y = index.row() - topRow
                        try:
                            if Globals.hex_grid.text[x][y] != None:
                                c = Globals.hex_grid.text[x][y]
                                return QtGui.QBrush(c.color)
                        except(IndexError):
                            # dbg("data(%d,%d)" % (x,y))
                            pass
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        if index.column() == Globals.hex_grid.width + 1:
            return Globals.main_window.read_txt(index.row() * Globals.hex_grid.width, Globals.hex_grid.width)
        if index.column() == 0:
            return "%08x" % (index.row() * Globals.hex_grid.width)
        return Globals.main_window.read_hex(index.row() * Globals.hex_grid.width + index.column() - 1)

    def headerData(self, col, orientation, role):
        return None

    def canFetchMore(self, parent):
        dbg("canFetchMore")
        return True

    def fetchMore(self, parent):
        dbg("fetchMore")
        dbg(parent)
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled


class MarkableGrid(QtWidgets.QTableView):
    (NEW_REGION, MERGE_REGIONS, RESIZE_REGION) = range(0, 3)

    def __init__(self, parent, width, height):
        Globals.hex_grid = self
        QtWidgets.QTableView.__init__(self)
        self.parent = parent
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)
        font = QtGui.QFont("Monospace", 8);
        font.setStyleHint(QtGui.QFont.TypeWriter);
        self.setFont(font);
        self.regions = MarkedRegions()
        self.all_references = ReferenceList()
        self.all_guessed_regions = set()
        self.view_regions = []
        self.width = width
        self.height = height
        self.text = None
        self.selection_model = None

    def mousePressEvent(self, event):
        dbg("mousePressEvent")
        dbg(event)
        super().mousePressEvent(event)
        rect = self.viewport().rect()
        index = self.currentIndex()
        topRow = Globals.hex_grid.indexAt(rect.topLeft()).row()
        x = index.column() - 1
        y = index.row() - topRow
        if self.text != None:
            if self.text[x] != None:
                if self.text[x][y] != None:
                    self.text[x][y].mousePressEvent(event)
                else:
                    dbg("text[%d][%d] is None" % (x,y))
            else:
                dbg("text[%d] is None" % x)
        else:
            dbg("text is None")

    def update_view(self):
        rect = self.viewport().rect()
        topRow = self.indexAt(rect.topLeft()).row()
        self.view_regions = []
        self.text = []
        Globals.main_window.pos = topRow * Globals.hex_grid.width
        self.calc_view_regions(Globals.main_window.pos, Globals.main_window.pos + self.width * self.height)
        for x in range(0, self.width):
            i = []
            self.text.append(i)
            for y in range(0, self.height):
                i.append(None)
        for rl in self.view_regions:
            for r in rl:
                (item, color) = r
                if color != None:
                    item.set_color(color)
                    self.text[item.x][item.y] = item

    def on_scroll(self, *args):
        dbg("scroll_to")
        dbg(args)
        self.update_view()

    def update(self):
        i1 = QtCore.QModelIndex()
        i2 = QtCore.QModelIndex()
        self.dataChanged(i1, i2, [])
        self.model = MyTableModel(self)
        self.selection_model = MySelectionModel(self.model)
        self.setModel(self.model)
        self.setSelectionModel(self.selection_model)

        MARGIN = 8
        CHAR_WIDTH = 7
        OFFSET_WIDTH = MARGIN + CHAR_WIDTH * 8
        TEXT_WIDTH = MARGIN + CHAR_WIDTH * self.width
        COL_WIDTH = MARGIN + CHAR_WIDTH * 2
        SCROLLBAR_WIDTH = 8
        self.setColumnWidth(0, OFFSET_WIDTH)
        self.setColumnWidth(self.width + 1, TEXT_WIDTH)
        for i in range(1, self.width + 1):
            self.setColumnWidth(i, COL_WIDTH)
        for i in range(0, self.height):
            self.setRowHeight(i, 24)
        self.setMinimumWidth(SCROLLBAR_WIDTH + OFFSET_WIDTH + TEXT_WIDTH + (self.width) * COL_WIDTH)
        self.setMinimumHeight((2 + self.height) * 24)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def load(self):
        self.regions.load()

    def save(self):
        self.regions.save()

    def reset_regions(self):
        self.regions = MarkedRegions()
        self.view_regions = []

    def calc_view_regions(self, start_pos, end_pos):
        dbg("calc_view_regions %08x,%08x" % (start_pos, end_pos))
        regions_in_view = self.regions.find_within(start_pos, end_pos)
        region_entry_list = []
        for r in regions_in_view:
            for y in range(0, self.height):
                for x in range(0, self.width):
                    i = Globals.main_window.pos + y * self.width + x
                    if i >= r.start_pos and i <= r.end_pos:
                        region_entry_list.append((
                        MarkableCell(self, x, y), r.get_color(i, Globals.main_window.read_txt(y * self.width + x, 1))))
        if Globals.main_window.action_References.isChecked():
            dbg("searching references in view starting at: %08x and ending at %08x(count of references: %d,referenceList:%s)" %  (Globals.main_window.pos,Globals.main_window.pos+self.width*self.height,len(self.all_references),type(self.all_references)))
            for y in range(0, self.height):
                for x in range(0, self.width):
                    i = Globals.main_window.pos + y * self.width + x
                    found_ref = False
                    found_guess = False
                    if (i  in self.all_references):
                        dbg("%08x" % i)
                        region_entry_list.append((MarkableCell(self, x, y), QtGui.QColor(0x00FF00)))
                        found_ref = True
                    elif (i  in self.all_guessed_regions):
                        region_entry_list.append((MarkableCell(self, x, y), QtGui.QColor(0x2222FF)))
                        found_guess = True
                    if found_guess:
                        dbg("found guessed region in view ,coloring cell at %d,%d" % (x,y))
                    if found_ref:
                        dbg("found reference in view ,coloring cell at %d,%d" % (x,y))
        dbg("region_entry_list : %d" % len(region_entry_list))
        self.view_regions.append(region_entry_list)

    def resize_region(self, region, newstart_pos, newend_pos):
        dbg("resize_region %08x %08x" % (newstart_pos, newend_pos))
        if newstart_pos != region.start_pos:
            for ref in region.references:
                self.all_references.remove(ref)
        Globals.r_searcher.get_ref(region).set_fully_scanned(False)
        region.start_pos = newstart_pos
        region.end_pos = newend_pos
        region.references = []

    def merge_regions(self, regions, start_pos, end_pos):
        dbg("merge_regions")
        start_poses = []
        end_poses = []
        start_poses.append(start_pos)
        end_poses.append(end_pos)
        for r in regions:
            start_poses.append(r.start_pos)
            end_poses.append(r.end_pos)
        start_pos = min(start_poses)
        end_pos = max(end_poses)
        newRegion = MarkedRegion(start_pos, end_pos - start_pos)
        for r in regions:
            newRegion.properties.extend(r.properties)
        for r in regions:
            self.regions.remove(r)
        self.regions.append(newRegion)

    def new_region(self, start_pos, end_pos):
        dbg("%d,%d" % (start_pos, end_pos))
        r = MarkedRegion(start_pos, end_pos - start_pos)
        self.regions.add(r)


    def detect_region_action(self, start_pos, end_pos):
        regions = self.regions.find_within(start_pos, end_pos)
        if (len(regions) == 0):
            dbg("NEW_REGION")
            return (MarkableGrid.NEW_REGION, None)
        elif (len(regions) > 1):
            dbg("MERGE_REGION")
            return (MarkableGrid.MERGE_REGIONS, regions)
        elif (len(regions) == 1):
            dbg("RESIZE_REGION")
            return (MarkableGrid.RESIZE_REGION, regions[0])

    def get_start_end_sel(self):
        x2 = None
        y2 = None
        x1 = None
        y1 = None
        for x in self.selectedIndexes():
            if (x1 is None) or (y1 is None) or (x.row() < y1):
                y1 = x.row()
                x1 = x.column()
            elif (x2 is None) or (x.row() == y1) and (x.column() < x1):
                x2 = x.column()
            if (x2 is None) or (y2 is None) or (x.row() > y2):
                y2 = x.row()
                x2 = x.column()
            elif (x2 is None) or (x.row() == y2) and (x.column() > x2):
                x2 = x.column()
        dbg("get_start_end_sel %d %d - %d %d" % (x1, y1, x2, y2))
        start_pos = (x1 - 1) + y1 * self.width
        end_pos = (x2 - 1) + y2 * self.width
        return (start_pos, end_pos)

    def store_region(self):
        (start_pos, end_pos) = self.get_start_end_sel()
        dbg("store_region %d-%d" % (start_pos, end_pos))
        (action, result) = self.detect_region_action(start_pos, end_pos)
        if action == 0:
            self.new_region(start_pos, end_pos)
        elif action == 1:
            self.merge_regions(result, start_pos, end_pos)
        elif action == 2:
            self.resize_region(result, start_pos, end_pos)
        self.view_regions = []
        self.update_view()
        self.selection_model.clearSelection()
        Globals.r_searcher.invalidate_pointer_search(self.regions.region_list)

    def store_nullstring(self):
        dbg("store_nullstring")
        (start_pos, end_pos) = self.get_start_end_sel()
        regions = self.regions.find_within(start_pos, end_pos)
        dbg("len(regions): %d" % len(regions))
        if len(regions) != 1:
            dbg("%d region found" % len(regions))
            return
        r = regions[0]
        r.add_nullstring(start_pos)
        self.selection_model.clearSelection()

    def store_string(self):
        (start_pos, end_pos) = self.get_start_end_sel()
        regions = self.regions.find_within(start_pos, end_pos)
        self.selection_model.clearSelection()
        if len(regions) != 1:
            return

    def delete_region(self, region):
        dbg("delete_region")
        for ref in region.references:
            self.all_references.remove(ref)
        self.regions.remove(region)

    def erase(self):
        (start_pos, end_pos) = self.get_start_end_sel()
        dbg("erase %08x %08x" % (start_pos, end_pos))
        regions = self.regions.find_within(start_pos, end_pos)
        self.selection_model.clearSelection()
        if len(regions) != 1:
            dbg("%d region found" % len(regions))
            return
        region = regions[0]
        dbg("region %08x %08x" % (region.start_pos, region.end_pos))
        if (start_pos <= region.start_pos) and (end_pos >= region.end_pos):
            self.delete_region(region)
        else:
            if (start_pos <= region.start_pos) and (end_pos < region.end_pos):
                self.resize_region(region, end_pos + 1, region.end_pos)
            elif (start_pos > region.start_pos) and (end_pos >= region.end_pos):
                self.resize_region(region, region.start_pos, start_pos - 1)
        self.view_regions = []
        self.update_view()
        self.selection_model.clearSelection()

    def clear_selection(self):
        self.selection_model.clearSelection()

    def temp_select(self, start_pos, length):
        length -= 1

        x1 = start_pos % self.width
        y1 = int((start_pos - x1) / self.width)
        x1 += 1

        end_pos = start_pos + length
        if (end_pos % (self.width + 2) == 0):
            end_pos += 1
        x2 = end_pos % self.width
        y2 = int((end_pos - x2) / self.width)
        x2 += 1

        dbg("temp_select %d,%d - %d,%d (%d to %d)" % (x1, y1, x2, y2, start_pos, end_pos))
        first = self.model.index(y1, x1, QtCore.QModelIndex())
        last = self.model.index(y2, x2, QtCore.QModelIndex())
        selected_items = CustomSelection(first, last)
        self.selection_model.clearSelection()
        self.selection_model.select(selected_items, QtCore.QItemSelectionModel.Select)

    def find_region_at(self, start_pos):
        reference = None
        show_refs = False
        if start_pos in self.all_references:
            for i in range(0,Globals.pointer_size):
                for r in self.all_references:
                    if r.address == start_pos - i:
                        dbg("%08x was in reference list." % (start_pos - i))
                        reference = Globals.r_searcher.calculate_pointer_pos_rva(start_pos - i)
                        show_refs = True
                        dbg("reference %s." % reference)
                        break
                if show_refs:
                    break
        else:
            dbg("%08x not in reference list." % start_pos)
        r = self.regions.find_region_containing(start_pos, start_pos)
        return r, reference, show_refs

class MarkableCell(QtWidgets.QWidget):
    def __init__(self, parent, x, y):
        super(MarkableCell, self).__init__()
        self.parent = parent
        self.x = x
        self.y = y
        self.color = QtGui.QColor(0xFFFFFF)
        self.parent = parent

    def set_color(self, color):
        self.color = color

    def mousePressEvent(self, event):
        dbg("mousePressEvent")
        if (event.button() == QtCore.Qt.RightButton):
            start_pos = Globals.main_window.pos + self.y * Globals.hex_grid.width + self.x
            r, reference, show_refs = Globals.hex_grid.find_region_at(start_pos)
            Globals.properties_window.show_refs = show_refs
            Globals.properties_window.ref = reference
            if len(r) > 0:
                Globals.properties_window.show(r[0])
            else:
                if show_refs:
                    Globals.properties_window.show(None)
