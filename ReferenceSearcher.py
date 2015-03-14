import time
from PyQt5         import QtCore, QtGui
from struct        import *
from MarkedRegions import *
import Globals
from   Globals     import *

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
        dbg("run")
        while True:
            time.sleep(10)
            if self.file == None:
                continue
            if Globals.hexGrid == None:
                break;
            searchRegions = []
            if len(Globals.hexGrid.regions.regionList)>0:
                dbg("processing")
                for r in Globals.hexGrid.regions.regionList:
                    if not r.fullyScanned:
                        searchRegions.append(r)
                if len(searchRegions)>0 :
                    self.pos = 0
                    self.searchAll(searchRegions)
                time.sleep(1)
            allRefs = ReferenceList()
            if len(Globals.hexGrid.regions.regionList)>0:
                for r in Globals.hexGrid.regions.regionList:
                    allRefs.extend(r.references)
            Globals.hexGrid.allReferences = allRefs
            self.pos = 0
            self.guessRegions(Globals.hexGrid.allReferences)
            Globals.hexGrid.allGuessedRegions = []
            for ref in Globals.hexGrid.allReferences:
                Globals.hexGrid.allGuessedRegions.extend(ref.guessedRegions)
        dbg("stopped")

    def calculatePointerPosRVA(self,pos):
        dbg("calculatePointerPosRVA(%08x)" % pos)
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
                dbg("calculateRVAByVirt(%08x) returned %08x" % (vPos,pos))
                return pos
        dbg("calculateRVAByVirt: nothing found for %08x" % (vPos,))
        
    def calculateSearchDataByRva(self,data):
        if type(data) is MarkedRegion:
            region = data
            pos    = region.startPos
        else:
            pos    = data
        for (rva,vaddr,size) in Globals.mainWindow.rvaList:
            if pos>=rva and pos<=rva+size:
                dbg("calculated %08x to %08x (Frame %08x,%08x,%08x)" % (pos,pos-rva+vaddr,rva,vaddr,size))
                if type(data) is MarkedRegion:                
                    region.virtualPos = pos-rva+vaddr
                return pack("<I",pos-rva+vaddr)
        dbg("not calculated,using plain %08x" % (pos,))
        if type(data) is MarkedRegion:
            region.virtualPos = pos
        return pack("<I",pos)
        
    def searchAll(self,regions):
        dbg("rSearcher.searchNext")
        Globals.mainWindow.statusBar().showMessage('Recalculating all references')
        searchDataList = []
        for r in regions:
            if r.fullyScanned:
                continue
            searchData = self.calculateSearchDataByRva(r)
            searchDataList.append(searchData)
        while self.pos<self.size-self.searchDataSize:
            self.file.seek(self.pos)
            buf           = self.file.read(self.file.cacheSize)
            time.sleep(1)
            n = 0
            for r in regions:
                if r.fullyScanned:
                    continue
                time.sleep(0.1)
                n = 0
                try:
                    searchData   = searchDataList[n]
                    n           += 1
                    p            = n+buf[n:].index(searchData)
                    n            = p+1
                    if self.pos+p not in r.references:
                        dbg("append reference %08x" %(self.pos+p))
                        r.references.append(Reference(self.pos+p))
                except(ValueError):
                    pass
            self.pos += len(buf)-self.searchDataSize
        for r in regions:
            r.fullyScanned = True
        self.parent.statusBar().showMessage('Ready')

    def guessRegions(self,references):
        dbg("guessRegions (%d references)" % len(references))
        doScan = False
        cnt    = 0
        for r in references:
            if not r.fullyScanned:
                doScan = True
        if doScan:
            searchDataList = []
            for r in references:
                if r.fullyScanned:
                    continue
                searchData = []
                for i in range(0,32):
                    searchData.append((i,self.calculateSearchDataByRva(r.addr-i)))
                searchDataList.append(searchData)
            while self.pos<self.size-self.searchDataSize:
                dbg("%08x/%08x" % (self.pos,self.size-self.searchDataSize))
                self.file.seek(self.pos)
                buf           = self.file.read(self.file.cacheSize)
                n             = 0
                time.sleep(1)
                for r in references:
                    if r.fullyScanned:
                        continue
                    
                    searchData = searchDataList[n]
                    n += 1
                    for (i,s) in searchData:
                        time.sleep(0.01)
                        try:
                            buf.index(s)
                            if r.addr-i not in r.guessedRegions:
                                r.guessedRegions.append(r.addr-i)
                                cnt += 1
                                break
                        except(ValueError):
                            pass
                self.pos += len(buf)-self.searchDataSize
            for r in references:
                for gr in r.guessedRegions:
                    dbg("appended guessedRegion %08x" %(gr))
                r.fullyScanned = True
        else:
            dbg("doScan was false")
        dbg("end guessRegions (%d added)" % cnt)
        
