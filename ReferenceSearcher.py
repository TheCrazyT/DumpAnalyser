import time
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QMutex, QMutexLocker
from struct import *
from MarkedRegions import *
import Globals
from Globals import *

class ReferenceWrapper():
    def __init__(self,object):
        self.object = object
        self.fully_scanned = False
        self.pointers_fully_scanned = False
        self.scan_started = None
        self.scan_ended = None
        self.virtual_pos = None
        self.guessed_regions = []
    def get_object(self):
        return self.object
    def set_fully_scanned(self,value):
        self.fully_scanned = value
    def get_fully_scanned(self):
        return self.fully_scanned
    def get_pointers_fully_scanned(self):
        return self.pointers_fully_scanned
    def set_pointers_fully_scanned(self,value):
        self.pointers_fully_scanned = value
    def get_scan_started(self):
        return self.scan_started
    def set_scan_started(self,value):
        self.scan_started = value
    def get_scan_ended(self):
        return self.scan_ended
    def set_scan_ended(self,value):
        self.scan_ended = value
    def get_virtual_pos(self):
        return self.virtual_pos
    def set_virtual_pos(self,value):
        self.virtual_pos = value
    def get_guessed_regions(self):
        return self.guessed_regions

class ReferenceSearcher(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self.file = None
        self.pos = 0
        self.size = 0
        self.lock = QMutex()
        self.force_scan = False
        self.ref_map = {}
        # TODO 64-Bit support
        self.search_data_size = 4

    def __del__(self):
        self.wait()

    def run(self):
        dbg("run")
        while True:
            time.sleep(10)
            with QMutexLocker(self.lock):
                Globals.main_window.statusBar().showMessage('Recalculating all references')
                while True:
                    if self.file == None:
                        continue
                    if Globals.hex_grid == None:
                        break;
                    search_regions = []
                    if len(Globals.hex_grid.regions.region_list) > 0:
                        dbg("processing")
                        for r in Globals.hex_grid.regions.region_list:
                            ref = self.get_ref(r)
                            if not ref.get_fully_scanned():
                                search_regions.append(r)
                        if len(search_regions) > 0:
                            self.pos = 0
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
                            self.pos = 0
                            self.search_all_pointers(search_regions, all_refs)
                        time.sleep(Globals.SLEEP_BETWEEN_REGIONS)
                    Globals.hex_grid.all_references = all_refs
                    self.pos = 0
                    self.guess_regions(all_refs)
                    Globals.hex_grid.all_guessed_regions = []
                    for ref in Globals.hex_grid.all_references:
                        sref = Globals.r_searcher.get_ref(ref)
                        Globals.hex_grid.all_guessed_regions.extend(sref.get_guessed_regions())
                    if self.force_scan:
                        self.force_scan = False
                    else:
                        break
                self.parent.statusBar().showMessage('Ready')
        dbg("stopped")

    def calculate_pointer_pos_rva(self, pos):
        dbg("calculatePointerPosRVA(%08x)" % pos)
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
        for (rva, vaddr, size) in Globals.main_window.rva_list:
            if v_pos >= vaddr and v_pos <= vaddr + size:
                pos = v_pos - vaddr + rva
                dbg("calculate_rva_by_virt(%08x) returned %08x" % (v_pos, pos))
                return pos
        dbg("calculate_rva_by_virt: nothing found for %08x" % (v_pos,))

    def calculate_virt_by_rva(self, pos):
        for (rva, vaddr, size) in Globals.main_window.rva_list:
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
        vPos = self.calculate_virt_by_rva(pos)
        if vPos != None:
            dbg("calculated %08x to %08x" % (pos, vPos,))
            if type(data) is MarkedRegion:
                ref = self.get_ref(data)
                ref.set_virtual_pos(vPos)
            return pack("<I", vPos)
        dbg("not calculated,using plain %08x" % (pos,))
        if type(data) is MarkedRegion:
            ref = self.get_ref(data)
            ref.set_virtual_pos(pos)
        return pack("<I", pos)

    def search_all(self, regions):
        dbg("rSearcher.searchNext")
        search_data_list = []
        for r in regions:
            ref = self.get_ref(r)
            if ref.get_fully_scanned():
                continue
            search_data = self.calculate_search_data_by_rva(r)
            search_data_list.append(search_data)
        while self.pos < self.size - self.search_data_size:
            self.file.seek(self.pos)
            buf = self.file.read(self.file.cache_size)
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
                    p = buf.index(search_data)
                    if self.pos + p not in r.references:
                        dbg("append reference %08x" % (self.pos + p))
                        r.references.append(Reference(self.pos + p))
                except(ValueError):
                    pass
            self.pos += len(buf) - self.search_data_size
        for r in regions:
            ref = self.get_ref(r)
            ref.set_fully_scanned(True)

    def guess_regions(self, references):
        dbg("guess_regions (%d references)" % len(references))
        doScan = False
        cnt = 0
        for r in references:
            ref = self.get_ref(r)
            if not ref.get_fully_scanned():
                doScan = True
        if doScan:
            search_data_list = []
            for r in references:
                ref = self.get_ref(r)
                if ref.get_fully_scanned():
                    continue
                search_data = []
                for i in range(0, 32):
                    search_data.append((i, self.calculate_search_data_by_rva(r.addr - i)))
                search_data_list.append(search_data)
            while self.pos < self.size - self.search_data_size:
                dbg("%08x/%08x" % (self.pos, self.size - self.search_data_size))
                self.file.seek(self.pos)
                buf = self.file.read(self.file.cache_size)
                n = 0
                time.sleep(Globals.SLEEP_BETWEEN_REGION_READ)
                for r in references:
                    ref = self.get_ref(r)
                    if ref.get_fully_scanned():
                        continue

                    search_data = search_data_list[n]
                    n += 1
                    for (i, s) in search_data:
                        time.sleep(Globals.SLEEP_BETWEEN_REGION_SCAN)
                        try:
                            buf.index(s)
                            if r.addr - i not in ref.get_guessed_regions():
                                ref.get_guessed_regions().append(r.addr - i)
                                cnt += 1
                                break
                        except(ValueError):
                            pass
                self.pos += len(buf) - self.search_data_size
            for r in references:
                ref = self.get_ref(r)
                for gr in ref.get_guessed_regions():
                    dbg("appended guessed_region %08x" % (gr))
                ref = self.get_ref(r)
                ref.set_fully_scanned(True)
        else:
            dbg("doScan was false")
        dbg("end guessRegions (%d added)" % cnt)

    def get_ref(self,o):
        try:
            return self.ref_map[o]
        except(KeyError):
            ref = ReferenceWrapper(o)
            self.ref_map[o] = ref
            return ref

    def reset_ref_map(self):
        self.ref_map = {}

    def invalidate_pointer_search(self, regions):
        for r in regions:
            ref = self.get_ref(r)
            ref.set_pointers_fully_scanned(False)

    def search_all_pointers(self, regions, all_references):
        for r in regions:
            for ref in all_references:
                time.sleep(Globals.SLEEP_BETWEEN_REGION_SCAN)
                if (r.start_pos <= ref.addr) and (r.end_pos >= ref.addr):
                    if ref not in r.pointers:
                        r.pointers.append(ref)
            ref = self.get_ref(r)
            ref.set_pointers_fully_scanned(True)
