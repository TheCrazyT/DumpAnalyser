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
        Globals.r_searcher.stop()
        Globals.r_searcher.destroy()
        if (self._opened_file != None):
            self._opened_file.close()

    def show_regions_window(self):
        Globals.regions_window.show()

    def show_rva_window(self):
        Globals.rva_window.show()

    def show_search_window(self):
        Globals.search_window.show(self._opened_file, self._file_size, self.search)

    def show_references_window(self):
        Globals.references_window.show()

    def refresh_references(self):
        self.statusBar().showMessage('Recalculating all references')

        Globals.hex_grid.all_references = ReferenceList()
        for r in Globals.hex_grid.regions.region_list:
            r.references = []
            ref = Globals.r_searcher.get_ref(r)
            ref.set_fully_scanned(False)

        Globals.r_searcher.signal_force_scan.emit()

    def search(self, pos):
        self.set_pos(pos)
        Globals.hex_grid.temp_select(pos, len(Globals.search_window.txtSearch.text()))
        Globals.hex_grid.setFocus()

    def do_load(self, filename):
        db.connect(filename)
        self._rva_list = db.load_rva_list()
        Globals.hex_grid.load()
        db.close()

    def do_save(self,filename):
        db.connect(filename)
        db.create_rva_list_tbl()
        db.create_regions_tbl()
        db.create_regions_ref_tbl()
        db.create_regions_prop_tbl()
        db.create_indexed_pages()
        db.save_rva_list(self._rva_list)
        Globals.hex_grid.save()
        db.save_indexed_pages()
        db.commit()
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
            self.do_save(filename)

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
        self._pos = pos
        y = int(self._pos / Globals.hex_grid.width)
        idx = Globals.hex_grid.model.index(y, 0, QtCore.QModelIndex())
        Globals.hex_grid.scrollTo(idx)

    def read_txt(self, pos, length):
        self._cached_file.seek(pos)
        s = self._cached_file.read(length)
        txt = ""
        for b in s:
            if (10 == b) or (13 == b) or (9 == b) or (chr(b) not in string.printable):
                txt += "."
            else:
                txt += chr(b)

        return txt

    def read_pointer(self, pos):
        self._cached_file.seek(pos)
        b = self._cached_file.read(Globals.pointer_size)
        return b

    def read_hex(self, pos):
        self._cached_file.seek(pos)
        b = self._cached_file.read(1)[0]
        return "%02x" % b

    def open_file(self, fname):
        self._opened_file = open(fname, "rb")
        self._opened_file.locker = None
        self._cached_file = CachedReader(self._opened_file)
        self._pos = 0
        self._file_size = os.path.getsize(fname)
        Globals.hex_grid.update()
        Globals.r_searcher.set_file(CachedReader(self._opened_file))
        Globals.r_searcher.set_size(self._file_size)

    def open_dlg(self):
        if not self._opened_file is None:
            self._opened_file.close()
        (filename, unknown) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open dump file', '.', '')
        if filename != "":
            self.open_file(filename)

    def get_rva_list(self):
        return self._rva_list

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Globals.main_window = self

        self._rva_list = []
        self._cached_file = None
        self._pos = 0
        self._file_size = 0

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

        self._opened_file = None
        self.statusBar().showMessage('Ready')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
