from PyQt5.QtCore    import Qt
from PyQt5.QtCore    import QMutex


CACHE_SIZE = 100*1024*1024
#CACHE_SIZE = 50000
class CachedReader:
    def __init__(self,file):
        self.file       = file
        self.cachePos   = None
        self.cacheSize  = CACHE_SIZE
        self.pos        = 0
        if(file.locker == None):
            self.file.locker = QMutex()

    def withinCache(self,size):
        if self.cachePos == None:
            return False
        if (self.pos>=self.cachePos)and(self.pos+size<=self.cachePos+self.cacheSize):
            return True
        return False

    def getFromCache(self,size):
        #print("CachedReader.getFromCache(%d)" % size)
        rpos      = self.pos - self.cachePos
        result    = self.cache[rpos:rpos+size]
        self.pos += size
        #print("returned %d bytes from %d bytes" % (len(result),len(self.cache)))
        return result

    def seek(self,pos):
        #print("CachedReader.seek(%08x)" % pos)
        self.pos = pos
        
    def read(self,size):
        #print("CachedReader.read(%d) from pos: %08x" % (size,self.pos))
        if(not self.withinCache(size)):
            self.file.locker.lock()
            orgPos = self.file.tell()
            
            self.file.seek(self.pos)
            self.cachePos = self.pos
            self.cache    = self.file.read(self.cacheSize)
            
            self.file.seek(orgPos)
            self.file.locker.unlock()
            #print("read %d bytes from %d bytes" % (len(self.cache),self.cacheSize))
        result = self.getFromCache(size)
        return result
    
    def close(self):
        self.file.close()
