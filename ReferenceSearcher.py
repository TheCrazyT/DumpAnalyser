import time
from PyQt5 import QtCore
from PyQt5.QtCore import QMutex, QMutexLocker,pyqtSignal
from MarkedRegions import MarkedRegion,Reference,ReferenceList
import Globals
from Globals import *
from Progress import Progress
from MarkableGrid import MarkableGrid

class ReferenceWrapper():
    def __init__(self,object):
        self._object = object
        self._fully_scanned = False
        self._pointers_fully_scanned = False
        self._scan_started = None
        self._scan_ended = None
        self._virtual_pos = None
        self._guessed_regions = set()
    def get_object(self):
        return self._object
    def set_fully_scanned(self,value):
        self._fully_scanned = value
    def get_fully_scanned(self):
        return self._fully_scanned
    def get_pointers_fully_scanned(self):
        return self._pointers_fully_scanned
    def set_pointers_fully_scanned(self,value):
        self._pointers_fully_scanned = value
    def get_scan_started(self):
        return self._scan_started
    def set_scan_started(self,value):
        self._scan_started = value
    def get_scan_ended(self):
        return self._scan_ended
    def set_scan_ended(self,value):
        self._scan_ended = value
    def get_address(self):
        return self._object.address
    def get_virtual_pos(self):
        return self._virtual_pos
    def set_virtual_pos(self,value):
        self._virtual_pos = value
    def get_guessed_regions(self):
        return self._guessed_regions

class ReferenceSearcher(QtCore.QThread):
    signal_stop_progress = pyqtSignal()
    signal_force_scan = pyqtSignal()
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self._parent = parent
        self._file = None
        self._pos = 0
        self._size = 0
        self._force_scan = False
        self._ref_map = {}
        self._indexed_pages = []
        # TODO 64-Bit support
        self._search_data_size = Globals.pointer_size
        self._progress = None
        self.signal_stop_progress.connect(self.stop_progress)
        self.signal_force_scan.connect(self.force_scan)

    def __del__(self):
        self.wait()

    def set_size(self,value):
        self._size = value

    def set_file(self,value):
        self._file = value

    def get_indexed_pages(self):
        return self._indexed_pages

    def set_indexed_pages(self,value):
        self._indexed_pages = value

    def reindex_pages(self):
        self._indexed_pages = []
        self.index_pages()

    def index_pages(self):
        dbg("paging through ... size:%d , page_size:%d" % (self._size,self._file.cache_size))
        k = 0
        for i1 in range(0,self._size,self._file.cache_size):
            k += 1
            if len(self._indexed_pages)>=k:
                dbg("page:%d was already indexed" % k)
                continue
            page = set()
            buf = self._file.read(self._file.cache_size)
            for i2 in range(0,len(buf)):
                if i2+1<len(buf):
                    v = buf[i2] * 0x100 + buf[i2+1]
                    #dbg("%06x" % v)
                    page.add(v)
                    time.sleep(Globals.SLEEP_BETWEEN_PAGE_VALUE)
            dbg("page:%d" % k)
            self._indexed_pages.append(page)
        dbg("done paging through")

    def is_value_in_page(self,value,page_pos):
        if(len(self._indexed_pages)==0):
            return True
        page = self._indexed_pages[page_pos]
        return value in page

    def stop_progress(self):
        grid = Globals.hex_grid
        assert isinstance(grid,MarkableGrid)
        grid.setEnabled(True)
        Globals.r_searcher._force_scan = False
        progress = Globals.r_searcher._progress
        assert isinstance(progress,Progress)
        progress.close()
        Globals.r_searcher._progress = None
        dbg("Lock stoppped.")
        Globals.SLEEP_BETWEEN_REGION_READ = Globals.r_searcher.tmp_sbrr
        Globals.SLEEP_BETWEEN_REGION_SCAN = Globals.r_searcher.tmp_sbrs
        Globals.SLEEP_BETWEEN_REGIONS = Globals.r_searcher.tmp_sbr
        Globals.SLEEP_BETWEEN_PAGE_VALUE = Globals.r_searcher.tmp_sbpv

    def force_scan(self):
        self.tmp_sbrr = Globals.SLEEP_BETWEEN_REGION_READ
        self.tmp_sbrs = Globals.SLEEP_BETWEEN_REGION_SCAN
        self.tmp_sbr = Globals.SLEEP_BETWEEN_REGIONS
        self.tmp_sbpv = Globals.SLEEP_BETWEEN_PAGE_VALUE
        Globals.SLEEP_BETWEEN_REGION_READ = 0
        Globals.SLEEP_BETWEEN_REGION_SCAN = 0
        Globals.SLEEP_BETWEEN_REGIONS = 0
        Globals.SLEEP_BETWEEN_PAGE_VALUE = 0
        grid = Globals.hex_grid
        assert isinstance(grid,MarkableGrid)
        grid.setEnabled(False)
        self._progress = Progress(None)
        progress_bar = self._progress
        assert isinstance(progress_bar,Progress)
        progress_bar.value_changed.emit(0)
        self._progress.on_stop_signal = self.signal_stop_progress
        self._progress.show()
        self._force_scan = True

    def run(self):
        dbg("run")
        while True:
            time.sleep(10)
            Globals.main_window.statusBar().showMessage('Recalculating all references')
            if self._progress:
                self._progress.description_changed.emit('Recalculating all references.')
            while True:
                if self._file is None:
                    continue
                if Globals.hex_grid is None:
                    break;
                self.index_pages()
                search_regions = []
                if len(Globals.hex_grid.regions.region_list) > 0:
                    dbg("processing")
                    for r in Globals.hex_grid.regions.region_list:
                        ref = self.get_ref(r)
                        if not ref.get_fully_scanned():
                            search_regions.append(r)
                    if len(search_regions) > 0:
                        self._pos = 0
                        self.search_all(search_regions)
                    time.sleep(Globals.SLEEP_BETWEEN_REGIONS)
                all_refs = ReferenceList()
                if len(Globals.hex_grid.regions.region_list) > 0:
                    for r in Globals.hex_grid.regions.region_list:
                        all_refs.extend(r.references)
                search_regions = []
                if len(Globals.hex_grid.regions.region_list) > 0:
                    for r in Globals.hex_grid.regions.region_list:
                        ref = self.get_ref(r)
                        if not ref.get_pointers_fully_scanned():
                            search_regions.append(r)
                    if len(search_regions) > 0:
                        self._pos = 0
                        self.search_all_pointers(search_regions, all_refs)
                    time.sleep(Globals.SLEEP_BETWEEN_REGIONS)
                Globals.hex_grid.all_references = all_refs
                self._pos = 0
                self.guess_regions(all_refs)
                Globals.hex_grid.all_guessed_regions = set()
                for ref in Globals.hex_grid.all_references:
                    sref = Globals.r_searcher.get_ref(ref)
                    Globals.hex_grid.all_guessed_regions = Globals.hex_grid.all_guessed_regions.union(sref.get_guessed_regions())
                if self._force_scan:
                    self._force_scan = False
                    self._progress = None
                else:
                    break
            self._parent.statusBar().showMessage('Ready')
        dbg("stopped")

    def calculate_pointer_pos_rva(self, pos):
        dbg("calculate_pointer_pos_rva(%08x)" % pos)
        i = []
        buf = Globals.main_window.read_pointer(pos)
        i.append(buf[3])
        i.append(buf[2])
        i.append(buf[1])
        i.append(buf[0])
        p = 0
        for j in i:
            p <<= 8
            p += j
        return self.calculate_rva_by_virt(p)

    def calculate_rva_by_virt(self, v_pos):
        for (rva, vaddr, size) in Globals.main_window.get_rva_list():
            if v_pos >= vaddr and v_pos <= vaddr + size:
                pos = v_pos - vaddr + rva
                dbg("calculate_rva_by_virt(%08x) returned %08x" % (v_pos, pos))
                return pos
        dbg("calculate_rva_by_virt: nothing found for %08x" % (v_pos,))
        return None

    def calculate_virt_by_rva(self, pos):
        for (rva, vaddr, size) in Globals.main_window.get_rva_list():
            if pos >= rva and pos <= rva + size:
                v_pos = pos - rva + vaddr
                dbg("calculate_virt_by_rva(%08x) returned %08x" % (pos, v_pos))
                return v_pos
        dbg("calculate_virt_by_rva: nothing found for %08x" % (pos,))
        return None

    def calculate_search_data_by_rva(self, data):
        if type(data) is MarkedRegion:
            region = data
            pos = region.start_pos
        else:
            pos = data
        virtual_pos = self.calculate_virt_by_rva(pos)
        if virtual_pos != None:
            dbg("calculated %08x to %08x" % (pos, virtual_pos,))
            if type(data) is MarkedRegion:
                ref = self.get_ref(data)
                ref.set_virtual_pos(virtual_pos)
            return virtual_pos
        dbg("not calculated,using plain %08x" % (pos,))
        if type(data) is MarkedRegion:
            ref = self.get_ref(data)
            ref.set_virtual_pos(pos)
        return pos

    def get_page_by_pos(self):
        pos = self._pos
        pos = pos / self._file.cache_size
        return int(pos)

    def search_all(self, regions):
        dbg("rSearcher.searchNext")
        progress_bar = None
        if self._progress:
            progress_bar = self._progress
            assert isinstance(progress_bar,Progress)
            self._progress.description_changed.emit("Searching for references.")

        search_data_list = []
        for r in regions:
            ref = self.get_ref(r)
            if ref.get_fully_scanned():
                continue
            search_data = Globals.get_raw_pointer(self.calculate_search_data_by_rva(r))
            search_data_list.append(search_data)
        if progress_bar:
            progress_bar.maximum_changed.emit(self._size)
        while self._pos < self._size - self._search_data_size:
            if progress_bar:
                progress_bar.value_changed.emit(self._pos)
            self._file.seek(self._pos)
            buf = self._file.read(self._file.cache_size)
            time.sleep(Globals.SLEEP_BETWEEN_REGION_READ)
            k = 0
            for r in regions:
                ref = self.get_ref(r)
                if ref.get_fully_scanned():
                    continue
                time.sleep(Globals.SLEEP_BETWEEN_REGION_SCAN)
                try:
                    search_data = search_data_list[k]
                    k += 1

                    page_pos = self.get_page_by_pos()
                    v = search_data[0]*0x100 + search_data[1]
                    if not self.is_value_in_page(v,page_pos):
                        continue

                    p = buf.index(search_data)
                    if self._pos + p not in r.references:
                        dbg("append reference %08x" % (self._pos + p))
                        r.references.append(Reference(self._pos + p))
                except(ValueError):
                    pass
            self._pos += len(buf)
        for r in regions:
            ref = self.get_ref(r)
            ref.set_fully_scanned(True)

    def guess_regions(self, references):
        dbg("guess_regions (%d references)" % len(references))
        progress_bar = None
        byte_map = 0xFF
        if self._progress:
            progress_bar = self._progress
            assert isinstance(progress_bar,Progress)
            progress_bar.description_changed.emit("Searching for guessed regions.")

        do_scan = False
        cnt = 0
        for r in references:
            ref = self.get_ref(r)
            if not ref.get_fully_scanned():
                do_scan = True
        if do_scan:
            search_data_list = []
            ref_list = [self.get_ref(r) for r in references if not self.get_ref(r).get_fully_scanned()]
            for ref in ref_list:
                search_data = dict()
                for i in range(0, 32):
                    pointer = self.calculate_search_data_by_rva(ref.get_address() - i)
                    raw_pointer = Globals.get_raw_pointer(pointer)
                    search_data[pointer] = (i,raw_pointer)
                search_data_list.append(search_data)
            buf_val = bytearray()
            buf_val_hashable = 0
            k = 0
            if progress_bar:
                progress_bar.maximum_changed.emit(self._size)
            while self._pos < self._size - self._search_data_size:
                dbg("%08x/%08x" % (self._pos, self._size - self._search_data_size))
                if progress_bar:
                    progress_bar.value_changed.emit(self._pos)
                self._file.seek(self._pos)
                buf = self._file.read(self._file.cache_size)
                time.sleep(Globals.SLEEP_BETWEEN_REGION_READ)
                for b in buf:
                    search_data_index = 0
                    k += 1

                    buf_val_hashable >>= 8
                    buf_val_hashable ^= b << (8*(Globals.pointer_size-1))

                    buf_val.append(b)

                    if k-1 < Globals.pointer_size:
                        continue

                    l = len(buf_val)
                    buf_val = buf_val[l-Globals.pointer_size:l]
                    for ref in ref_list:
                        search_data = search_data_list[search_data_index]
                        search_data_index += 1
                        if buf_val_hashable in search_data:
                            lst = [search_data[s][0] for s in search_data if (search_data[s][1] == buf_val) and (ref.get_address() - search_data[s][0] not in ref.get_guessed_regions())]
                            for i in lst:
                                ref.get_guessed_regions().add(r.address - i)
                                cnt += 1
                                break
                if len(buf) == 0:
                    self._pos += 1
                else:
                    self._pos += len(buf)
            for r in references:
                ref = self.get_ref(r)
                for gr in ref.get_guessed_regions():
                    dbg("appended guessed_region %08x" % (gr))
                ref.set_fully_scanned(True)
        else:
            dbg("do_scan was false")
        dbg("end guessRegions (%d added)" % cnt)

    def get_ref(self,o):
        try:
            return self._ref_map[o]
        except(KeyError):
            ref = ReferenceWrapper(o)
            self._ref_map[o] = ref
            return ref

    def reset_ref_map(self):
        self._ref_map = {}

    def invalidate_pointer_search(self, regions):
        for r in regions:
            ref = self.get_ref(r)
            ref.set_pointers_fully_scanned(False)

    def search_all_pointers(self, regions, all_references):
        if self._progress:
            self._progress.description_changed.emit('Searching all pointers.')
        for r in regions:
            for ref in all_references:
                time.sleep(Globals.SLEEP_BETWEEN_REGION_SCAN)
                if (r.start_pos <= ref.address) and (r.end_pos >= ref.address):
                    if ref not in r.pointers:
                        r.pointers.append(ref)
            ref = self.get_ref(r)
            ref.set_pointers_fully_scanned(True)
