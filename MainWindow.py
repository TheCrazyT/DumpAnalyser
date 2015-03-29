#!/usr/bin/env python
import sys
import os
import db
import time
import string
import Globals
from   Globals import *
from struct import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QMutex, QMutexLocker
from MarkableGrid import *
from ToolMenu import *

from RegionsWindow import *
from ReferencesWindow import *
from RvaWindow import *
from SearchWindow import *
from PropertiesWindow import *

from ReferenceSearcher import *
from CachedReader import *

MainWindowUI = uic.loadUiType("mywindow.ui")[0]


class MainWindow(QtWidgets.QMainWindow, MainWindowUI):
    def delete_event(self, widget, event, data=None):
        return False

    def quit_window(self):
        sys.exit(0)

    # Another callback
    def destroy(self, widget, data=None):
        self.r_searcher.stop()
        self.r_searcher.destroy()
        if (self.opened_file != None):
            self.opened_file.close()

    def show_regions_window(self):
        Globals.regions_window.show()

    def show_rva_window(self):
        Globals.rva_window.show()

    def show_search_window(self):
        Globals.search_window.show(self.opened_file, self.file_size, self.search)

    def show_references_window(self):
        Globals.references_window.show()

    def refresh_references(self):
        self.statusBar().showMessage('Recalculating all references')
        Globals.hex_grid.allReferences = []
        for r in Globals.hex_grid.regions.region_list:
            r.references = []
            r.fully_scanned = False
        tmp_sbrr = Globals.SLEEP_BETWEEN_REGION_READ
        tmp_sbrs = Globals.SLEEP_BETWEEN_REGION_SCAN
        tmp_sbr = Globals.SLEEP_BETWEEN_REGIONS
        Globals.SLEEP_BETWEEN_REGION_READ = 0
        Globals.SLEEP_BETWEEN_REGION_SCAN = 0
        Globals.SLEEP_BETWEEN_REGIONS = 0
        Globals.r_searcher.forceScan = True
        time.sleep(11)
        with QMutexLocker(Globals.r_searcher.lock):
            time.sleep(1)
        Globals.SLEEP_BETWEEN_REGION_READ = tmp_sbrr
        Globals.SLEEP_BETWEEN_REGION_SCAN = tmp_sbrs
        Globals.SLEEP_BETWEEN_REGIONS = tmp_sbr

    def search(self, pos):
        self.set_pos(pos)
        Globals.hex_grid.temp_select(pos, len(Globals.search_window.txtSearch.text()))
        Globals.hex_grid.setFocus()

    def do_load(self, filename):
        db.connect(filename)
        self.rva_list = db.load_rva_list()
        Globals.hex_grid.load()
        db.close()

    def load(self):
        (filename, unknown) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './save', '*.sav')
        if filename != "":
            try:
                filename.index(".sav")
            except:
                filename = "%s.sav" % filename
            self.do_load(filename)

    def goto(self):
        pos = 0
        (posStr, ok) = QtWidgets.QInputDialog.getText(self, "Position",
                                                      "Enter position in hex:")
        if ok:
            pos = int(str(posStr), 16)
            self.set_pos(pos)

    def save(self):
        (filename, unknown) = QtWidgets.QFileDialog.getSaveFileName(self, 'save file', './save', '*.sav')
        if filename != "":
            try:
                filename.index(".sav")
            except:
                filename = "%s.sav" % filename
            try:
                os.remove(filename)
            except(FileNotFoundError):
                pass
            db.connect(filename)
            db.create_rva_list_tbl()
            db.create_regions_tbl()
            db.create_regions_ref_tbl()
            db.create_regions_prop_tbl()
            db.save_rva_list(self.rva_list)
            Globals.hex_grid.save()
            db.commit()
            db.close()

    def search_next(self):
        pos = Globals.search_window.search_next()
        if pos == -1:
            return
        realPos = pos
        pos -= pos % Globals.hex_grid.width
        self.set_pos(pos)
        Globals.hex_grid.temp_select(realPos, len(Globals.search_window.txtSearch.text()))
        Globals.hex_grid.setFocus()

    def set_pos(self, pos):
        pos -= pos % Globals.hex_grid.width
        self.pos = pos
        y = int(self.pos / Globals.hex_grid.width)
        idx = Globals.hex_grid.model.index(y, 0, QtCore.QModelIndex())
        Globals.hex_grid.scrollTo(idx)

    def read_txt(self, pos, length):
        self.cached_file.seek(pos)
        s = self.cached_file.read(length)
        txt = ""
        for b in s:
            if (10 == b) or (13 == b) or (9 == b) or (chr(b) not in string.printable):
                txt += "."
            else:
                txt += chr(b)

        return txt

    def read_pointer(self, pos):
        self.cached_file.seek(pos)
        b = self.cached_file.read(4)
        return b

    def read_hex(self, pos):
        self.cached_file.seek(pos)
        b = self.cached_file.read(1)[0]
        return "%02x" % b

    def open_file(self, fname):
        self.opened_file = open(fname, "rb")
        self.opened_file.locker = None
        self.cached_file = CachedReader(self.opened_file)
        self.pos = 0
        self.file_size = os.path.getsize(fname)
        Globals.hex_grid.update()
        Globals.r_searcher.file = CachedReader(self.opened_file)
        Globals.r_searcher.size = self.file_size

    def open_dlg(self):
        if (self.opened_file != None):
            self.opened_file.close()
        (filename, unknown) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open dump file', '.', '')
        if filename != "":
            self.open_file(filename)

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Globals.main_window = self

        self.rva_list = []
        self.cache_pos = None
        self.cache_size = None
        self.cache = None
        self.pos = 0
        self.file_size = 0

        Globals.r_searcher = ReferenceSearcher(self)
        Globals.hex_grid = MarkableGrid(self, 32, 32)
        Globals.tool_menu = ToolMenu(self)

        Globals.rva_window = RvaWindow(self)
        Globals.search_window = SearchWindow(self)
        Globals.regions_window = RegionsWindow(self)
        Globals.references_window = ReferencesWindow(self)
        Globals.properties_window = PropertiesWindow(self)

        Globals.r_searcher.start()

        main_layout = QtWidgets.QHBoxLayout()
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        main_layout.addWidget(Globals.hex_grid)
        main_layout.addWidget(Globals.tool_menu)

        self.setupUi(self)
        self.setCentralWidget(main_widget)

        self.opened_file = None
        self.statusBar().showMessage('Ready')

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
