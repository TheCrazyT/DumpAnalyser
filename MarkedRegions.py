import db
import Globals
from   Globals import *
from PyQt5 import QtCore, QtGui

lastId = 0

class ReferenceList(list):
    def __init__(self):
        self.range = QtCore.QItemSelectionRange()

    def __contains__(self,ref):
        addr = None
        if type(ref) is Reference:
            addr = ref.addr
        else:
            addr = ref

        width = Globals.hexGrid.width

        col = addr % width
        row = (addr - col) / width
        idx = self.model.createIndex(row,col)
        return self.range.contains(idx)

    def __add__(self, ref):
        addr = None
        if type(ref) is Reference:
            addr = ref.addr
        else:
            addr = ref

        width = Globals.hexGrid.width

        col1  = addr % width
        row1  = (addr - col1) / width

        col2  = addr % width
        row2  = (addr - col1) / width

        if row1+2<=row2:
           idx1 = self.model.createIndex(row1+1,0)
           idx2 = self.model.createIndex(row2-1,width)
           sr   = QtCore.QItemSelectionRange(idx1,idx2)
           self.range.append(sr)
        if row1<row2:
           idx1 = self.model.createIndex(row1,col1)
           idx2 = self.model.createIndex(row1,width)
           sr   = QtCore.QItemSelectionRange(idx1,idx2)
           self.range.append(sr)
           idx1 = self.model.createIndex(row2,0)
           idx2 = self.model.createIndex(row2,col2)
           sr   = QtCore.QItemSelectionRange(idx1,idx2)
           self.range.append(sr)
        super.add(ref)


def genNewId():
    global lastId
    lastId += 1
    return lastId + 1

class MarkedRegions():
    def __init__(self):
        self.regionList = []
        
    def add(self,region):
        self.regionList.append(region)
        
    def append(self,region):
        self.regionList.append(region)

    def remove(self,region):
        self.regionList.remove(region)

    def findWithin(self,startPos,endPos):
        dbg("findWithin %08x,%08x" % (startPos,endPos))
        result = []
        for r in self.regionList:
            if endPos       >= r.startPos and endPos   <= r.endPos:
                result.append(r)
            elif startPos   >= r.startPos and startPos <= r.endPos:
                result.append(r)
            elif r.startPos > startPos  and r.endPos   < endPos:
                result.append(r)
        return result

    def load(self):
        global lastId
        self.regionList = db.loadRegions()
        allRefs         = []
        for r in self.regionList:
            if r.id>lastId:
                lastId = r.id + 1
            allRefs.extend(r.references)
        dbg(allRefs)
        Globals.hexGrid.allReferences = allRefs
        
    def save(self):
        for r in self.regionList:
            r.save()

class MarkedRegion():
    def __init__(self,startPos,length,id=None,color="red",fullyScanned=False,pointersFullyScanned=False):
        if id==None:
            id = genNewId()
        self.id           = id
        self.startPos     = startPos
        self.length       = length
        self.endPos       = startPos + length
        self.color        = color
        self.properties   = []
        self.pointers     = []
        self.references   = ReferenceList()
        self.fullyScanned         = fullyScanned
        self.pointersFullyScanned = pointersFullyScanned
        self.virtualPos           = None

    def save(self):
        db.saveRegion(self)

    def add_nullstring(self,pos):
        self.properties.append(NullString(pos))

    def get_color(self,pos,char):
        for p in self.properties:
            c = p.get_color(pos,char)
            if c != None:
                return c
        if pos == self.startPos:
            return QtGui.QColor(0xFF9999)
        if pos == self.endPos:
            return QtGui.QColor(0xFF6666)
        return QtGui.QColor(0xFF0000)

class NullString():
    def __init__(self,startPos):
        self.startPos = startPos
        self.endPos   = -1
    def get_color(self,pos,char):
        #dbg("NullString get_color %d %d| %d %d" % (pos,char,self.startPos,self.endPos))
        if self.endPos == -1:
            if pos>=self.startPos:
                if char == 0:
                    self.endPos = pos
                return QtGui.QColor(0x00FFFF)
        else:
            if (pos>=self.startPos) and (pos<=self.endPos):
                return QtGui.QColor(0x00FFFF)
        return None

class Reference():
    def __init__(self,addr,fullyScanned=False):
        self.addr           = addr
        self.fullyScanned   = fullyScanned
        self.guessedRegions = []
