from PyQt5.QtCore import Qt
from PyQt5.QtCore import QMutex
from   Globals import *

CACHE_SIZE = 100 * 1024 * 1024
# CACHE_SIZE = 50000
class CachedReader:
    def __init__(self, file):
        self.file = file
        self.cache_pos = None
        self.cache_size = CACHE_SIZE
        self.pos = 0
        if (file.locker == None):
            self.file.locker = QMutex()

    def within_cache(self, size):
        if self.cache_pos == None:
            return False
        if (self.pos >= self.cache_pos) and (self.pos + size <= self.cache_pos + self.cache_size):
            return True
        return False

    def get_from_cache(self, size):
        #dbg("CachedReader.getFromCache(%d)" % size)
        rpos = self.pos - self.cache_pos
        result = self.cache[rpos:rpos + size]
        self.pos += size
        #dbg("returned %d bytes from %d bytes" % (len(result),len(self.cache)))
        return result

    def seek(self, pos):
        #dbg("CachedReader.seek(%08x)" % pos)
        self.pos = pos

    def read(self, size):
        #dbg("CachedReader.read(%d) from pos: %08x" % (size,self.pos))
        if (not self.within_cache(size)):
            self.file.locker.lock()
            orgPos = self.file.tell()

            self.file.seek(self.pos)
            self.cache_pos = self.pos
            self.cache = self.file.read(self.cache_size)

            self.file.seek(orgPos)
            self.file.locker.unlock()
            #dbg("read %d bytes from %d bytes" % (len(self.cache),self.cacheSize))
        result = self.get_from_cache(size)
        return result

    def close(self):
        self.file.close()
