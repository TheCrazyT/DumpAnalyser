import sys
import os
from ReferenceSearcher import *
from MarkedRegions     import *

if __name__ == "__main__":
    Globals.rSearcher  = ReferenceSearcher(None)
    regions       = []
    allReferences = ReferenceList()

    allReferences.append(Reference(60))

    r = MarkedRegion(50,100)
    regions.append(r)
    Globals.rSearcher.searchAllPointers(regions,allReferences)

    assert len(r.pointers)>0, "PointerList of region is empty!"
    
    sys.exit(0)
