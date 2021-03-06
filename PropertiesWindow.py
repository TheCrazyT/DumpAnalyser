from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals
from   Globals import *

(TYPE_REF, TYPE_REFS, TYPE_POINTER, TYPE_REGION) = range(0, 4)
PropertiesUI = uic.loadUiType("properties.ui")[0]


class PropertiesWindow(QtWidgets.QMainWindow, PropertiesUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.parent = parent
        self.show_refs = True
        self.ref = 0

    def goto_ref(self, pos, ptr_size):
        dbg("gotoRef")
        if (self.parent != None):
            Globals.main_window.set_pos(pos)
            Globals.hex_grid.temp_select(pos, ptr_size)

    def item_click(self, item):
        if item.type == TYPE_REGION:
            Globals.main_window.set_pos(item.data)
        if item.type == TYPE_REFS:
            self.goto_ref(item.data, 4)
        if item.type == TYPE_REF:
            Globals.main_window.set_pos(item.data)
        if item.type == TYPE_POINTER:
            Globals.main_window.set_pos(item.data)

    def show(self, region,show_window=True):
        self.tvProps.clear()
        if region != None:
            tli_ref = QtWidgets.QTreeWidgetItem()
            tli_ref.data = region.start_pos
            tli_ref.type = TYPE_REGION
            ref = Globals.r_searcher.get_ref(region)
            if ref.get_virtual_pos() == None:
                Globals.r_searcher.calculate_search_data_by_rva(region)
            tli_ref.setText(0, "References of %08x (%08x)" % (region.start_pos, ref.get_virtual_pos()))
            for r in region.references:
                tli = QtWidgets.QTreeWidgetItem()
                tli.type = TYPE_REFS
                tli.data = r.addr
                tli.setText(0, "%08x" % r.addr)
                tli_ref.addChild(tli)
            self.tvProps.addTopLevelItem(tli_ref)
            tli_ref.setExpanded(True)

            tli_ref = QtWidgets.QTreeWidgetItem()
            tli_ref.data = region.start_pos
            tli_ref.type = TYPE_REGION
            tli_ref.setText(0, "Pointers of %08x (%08x)" % (region.start_pos, ref.get_virtual_pos()))
            for p in region.pointers:
                tli = QtWidgets.QTreeWidgetItem()
                tli.type = TYPE_POINTER
                ref = Globals.r_searcher.calculate_pointer_pos_rva(p.addr)
                if ref != None:
                    vpos = Globals.r_searcher.calculate_virt_by_rva(ref)
                    if vpos != None:
                        tli.setText(0, "+%08x to %08x (%08x)" % (p.addr - region.start_pos, ref, vpos))
                        tli.data = ref
                        tli_ref.addChild(tli)
            self.tvProps.addTopLevelItem(tli_ref)
            tli_ref.setExpanded(True)

        if self.show_refs:
            if self.ref:
                tli_ref = QtWidgets.QTreeWidgetItem()
                vpos = Globals.r_searcher.calculate_virt_by_rva(self.ref)
                if vpos != None:
                    tli_ref.setText(0, "Selected reference leads to %08x (%08x)" % (self.ref, vpos))
                    tli_ref.type = TYPE_REF
                    tli_ref.data = self.ref
                    self.tvProps.addTopLevelItem(tli_ref)
                tli_ref.setExpanded(True)

        if show_window:
            super().show()
            super().activateWindow()
