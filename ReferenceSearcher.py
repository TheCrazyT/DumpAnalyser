import time
from PyQt5 import QtCore, QtGui
from struct import *
import Globals

class ReferenceSearcher(QtCore.QThread):
    def __init__(self,parent):
        QtCore.QThread.__init__(self)
        self.parent    = parent
        self.file      = None
        self.pos       = 0
        self.size      = 0
        #TODO 64-Bit support
        self.searchDataSize = 4

    def __del__(self):
        self.wait()

    def run(self):
        print("run")
        while True:
            time.sleep(10)
            if self.file == None:
                continue
            if Globals.hexGrid == None:
                break;
            searchRegions = []
            if len(Globals.hexGrid.regions.regionList)>0:
                print("processing")
                for r in Globals.hexGrid.regions.regionList:
                    if not r.fullyScanned:
                        searchRegions.append(r)
                if len(searchRegions)>0 :
                    self.pos = 0
                    self.searchAll(searchRegions)
                time.sleep(1)
            allRefs = []
            if len(Globals.hexGrid.regions.regionList)>0:
                for r in Globals.hexGrid.regions.regionList:
                    allRefs.extend(r.references)
            Globals.hexGrid.allReferences = allRefs
        print("stopped")

    def calculatePointerPosRVA(self,pos):
        print("calculatePointerPosRVA(%08x)" % pos)
        i    = []
        buf = Globals.mainWindow.readPointer(pos)
        i.append(buf[3])
        i.append(buf[2])
        i.append(buf[1])
        i.append(buf[0])
        p    = 0
        for j in i:
            p<<= 8
            p += j
        return self.calculateRVAByVirt(p)

    def calculateRVAByVirt(self,vPos):
        for (rva,vaddr,size) in Globals.mainWindow.rvaList:
            if vPos>=vaddr and vPos<=vaddr+size:
                pos = vPos-vaddr+rva
                print("calculateRVAByVirt(%08x) returned %08x" % (vPos,pos))
                return pos
        print("calculateRVAByVirt: nothing found for %08x" % (vPos,))
        
    def calculateSearchDataByRva(self,region):
        pos = region.startPos
        for (rva,vaddr,size) in Globals.mainWindow.rvaList:
            if pos>=rva and pos<=rva+size:
                print("calculated %08x to %08x (Frame %08x,%08x,%08x)" % (pos,pos-rva+vaddr,rva,vaddr,size))
                region.virtualPos = pos-rva+vaddr
                return pack("<I",pos-rva+vaddr)
        print("not calculated,using plain %08x" % (pos,))
        region.virtualPos = pos
        return pack("<I",pos)
        
    def searchAll(self,regions):
        print("rSearcher.searchNext")
        Globals.mainWindow.statusBar().showMessage('Recalculating all references')
        while self.pos<self.size-self.searchDataSize:
            self.file.seek(self.pos)
            buf           = self.file.read(self.file.cacheSize)
            time.sleep(1)
            for r in regions:
                time.sleep(0.1)
                n = 0
                try:
                    try:
                        if r.searchData == None:
                            r.searchData = self.calculateSearchDataByRva(r)
                    except(AttributeError):
                        r.searchData = self.calculateSearchDataByRva(r)
                    p            = n+buf[n:].index(r.searchData)
                    n            = p+1
                    if self.pos+p not in r.references:
                        print("append reference %08x" %(self.pos+p))
                        if self.pos+p not in r.references:
                            r.references.append(self.pos+p)
                except(ValueError):
                    pass
            self.pos += len(buf)-self.searchDataSize
        for r in regions:
            r.fullyScanned = True
        self.parent.statusBar().showMessage('Ready')
