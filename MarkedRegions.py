import db
import Globals
from Globals import *
from PyQt5 import QtCore, QtGui

last_id = 0


def get_col_row(address):
    width = Globals.hex_grid.width
    col = address % width
    row = (address - col) / width
    return col, row


def add_range(range, address, size):
    assert isinstance(range, QtCore.QItemSelection)
    width = Globals.hex_grid.width
    col1, row1 = get_col_row(address)
    col2, row2 = get_col_row(address + size)
    if row1 + 2 <= row2:
        idx1 = Globals.hex_grid.model.createIndex(row1 + 1, 0)
        idx2 = Globals.hex_grid.model.createIndex(row2 - 1, width)
        sr = QtCore.QItemSelectionRange(idx1, idx2)
        range.append(sr)
    if row1 < row2:
        idx1 = Globals.hex_grid.model.createIndex(row1, col1)
        idx2 = Globals.hex_grid.model.createIndex(row1, width)
        sr = QtCore.QItemSelectionRange(idx1, idx2)
        range.append(sr)
        idx1 = Globals.hex_grid.model.createIndex(row2, 0)
        idx2 = Globals.hex_grid.model.createIndex(row2, col2)
        sr = QtCore.QItemSelectionRange(idx1, idx2)
        range.append(sr)
    if row1 == row2:
        idx1 = Globals.hex_grid.model.createIndex(row1, col1)
        idx2 = Globals.hex_grid.model.createIndex(row1, col2-1)
        sr = QtCore.QItemSelectionRange(idx1, idx2)
        range.append(sr)


class ReferenceList(list):
    def __init__(self):
        list.__init__(self)
        self.range = QtCore.QItemSelection()

    def __contains__(self, ref):
        address = None
        if type(ref) is Reference:
            address = ref.address
        else:
            address = ref
        col, row = get_col_row(address)
        idx = Globals.hex_grid.model.createIndex(row, col)
        return self.range.contains(idx)

    def append(self, ref):
        address = None
        if type(ref) is Reference:
            address = ref.address
        else:
            address = ref
        dbg("add reference %08x to reference list" % (address))
        size = Globals.pointer_size
        add_range(self.range, address, size)
        super().append(ref)

    def extend(self, iterable):
        for i in iterable:
            self.append(i)

class RegionList(list):
    def __init__(self):
        list.__init__(self)
        self.range = QtCore.QItemSelection()

    def append(self, region):
        address = region.start_pos
        size = region.end_pos - region.start_pos
        add_range(self.range, address, size)
        super().append(region)

    def find_region_containing(self,start_pos,end_pos):
        #TODO (still buggy)
        sel = QtCore.QItemSelection()
        add_range(sel, start_pos, end_pos - start_pos + 1)
        has_intersect = False
        for r in sel:
            for r2 in self.range:
                if r2.intersects(r):
                    has_intersect = True
                    break
            if has_intersect:
                break
        result = []
        if has_intersect:
            for r in self:
                if end_pos >= r.start_pos and end_pos <= r.end_pos:
                    result.append(r)
                elif start_pos >= r.start_pos and start_pos <= r.end_pos:
                    result.append(r)
                elif r.start_pos > start_pos and r.end_pos < end_pos:
                    result.append(r)
            assert len(result)>0,"no region found although we had an intersect."
        return result

    def find_within(self, start_pos, end_pos):
        result = []
        for r in self:
            if r.start_pos>=start_pos and r.start_pos<=end_pos:
                result.append(r)
            elif r.end_pos>=start_pos and r.end_pos<=end_pos:
                result.append(r)
        return result


def gen_new_id():
    global last_id
    last_id += 1
    return last_id + 1


class MarkedRegions():
    def __init__(self):
        self.region_list = RegionList()

    def add(self, region):
        self.region_list.append(region)

    def append(self, region):
        self.region_list.append(region)

    def remove(self, region):
        self.region_list.remove(region)

    def find_region_containing(self,start_pos, end_pos):
        dbg("find_region_containing %08x,%08x" % (start_pos, end_pos))
        return self.region_list.find_region_containing(start_pos, end_pos)

    def find_within(self, start_pos, end_pos):
        dbg("find_within %08x,%08x" % (start_pos, end_pos))
        return self.region_list.find_within(start_pos, end_pos)

    def load(self):
        global last_id
        self.region_list = db.load_regions()
        all_refs = ReferenceList()
        for r in self.region_list:
            if r.id > last_id:
                last_id = r.id + 1
            all_refs.extend(r.references)
        dbg(all_refs)
        Globals.hex_grid.all_references = all_refs

    def save(self):
        for r in self.region_list:
            r.save()


class MarkedRegion():
    def __init__(self, start_pos, length, id=None):
        if id == None:
            id = gen_new_id()
        self.id = id
        self.start_pos = start_pos
        self.length = length
        self.end_pos = start_pos + length
        self.properties = []
        self.pointers = []
        self.references = ReferenceList()
        self.name = None
        self.color = None

    @staticmethod
    def __db_columns__():
        setters = {}
        getters = {}

        setters["color"] = "set_color"
        setters["name"] = "set_name"

        getters["color"] = "get_color_value"
        getters["id"] = "get_id"
        getters["startPos"] = "get_start_pos"
        getters["length"] = "get_length"
        getters["name"] = "get_name"

        return (setters,getters)

    def get_id(self):
        return self.id

    def get_color_value(self):
        return self.color

    def get_start_pos(self):
        return self.start_pos

    def get_length(self):
        return self.length

    def get_name(self):
        return self.name

    def set_color(self,value):
        self.color = value

    def set_name(self,value):
        self.name = value

    def save(self):
        db.save_region(self)

    def add_nullstring(self, pos):
        self.properties.append(NullString(pos))

    def get_color(self, pos, char):
        for p in self.properties:
            c = p.get_color(pos, char)
            if c != None:
                return c
        if pos == self.start_pos:
            return QtGui.QColor(0xFF9999)
        if pos == self.end_pos:
            return QtGui.QColor(0xFF6666)
        return QtGui.QColor(0xFF0000)


class NullString():
    def __init__(self, start_pos):
        self.start_pos = start_pos
        self.end_pos = -1

    def get_color(self, pos, char):
        # dbg("NullString get_color %d %d| %d %d" % (pos,char,self.start_pos,self.end_pos))
        if self.end_pos == -1:
            if pos >= self.start_pos:
                if char == 0:
                    self.end_pos = pos
                return QtGui.QColor(0x00FFFF)
        else:
            if (pos >= self.start_pos) and (pos <= self.end_pos):
                return QtGui.QColor(0x00FFFF)
        return None


class Reference():
    def __init__(self, address):
        self.address = address
