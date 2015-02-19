import db
import Globals

lastId = 0

def genNewId():
    global lastId
    lastId += 1
    return lastId + 1

class MarkedRegions():
    def __init__(self):
        self.regionList = []
        
    def add(self,reg):
        self.regionList.append(reg)
        
    def findWithin(self,startPos,endPos):
        print("findWithin %d,%d" % (startPos,endPos))
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
        print(allRefs)
        Globals.hexGrid.allReferences = allRefs
        
    def save(self):
        for r in self.regionList:
            r.save()

class MarkedRegion():
    def __init__(self,startPos,length,id=None,color="red",fullyScanned=False,references=[]):
        if id==None:
            id = genNewId()
        self.id           = id
        self.startPos     = startPos
        self.length       = length
        self.endPos       = startPos + length
        self.color        = color
        self.properties   = []
        self.references   = references
        self.fullyScanned = fullyScanned
        self.virtualPos   = None

    def save(self):
        db.saveRegion(self)
        
    def add_nullstring(self,pos):
        self.properties.append(NullString(pos))

    def get_color(self,pos,char):
        for p in self.properties:
            c = p.get_color(pos,char)
            if c != None:
                return c
        return "red"

class NullString():
    def __init__(self,startPos):
        self.startPos = startPos
        self.endPos   = -1
    def get_color(self,pos,char):
        #print("NullString get_color %d %d| %d %d" % (pos,char,self.startPos,self.endPos))
        if self.endPos == -1:
            if pos>=self.startPos:
                if char == 0:
                    self.endPos = pos
                return "yellow"
        else:
            if (pos>=self.startPos) and (pos<=self.endPos):
                return "yellow"
        return None
