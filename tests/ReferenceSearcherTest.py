import sys
import os
from ReferenceSearcher import *
from MarkedRegions import *
import unittest

class ReferenceSearcherTest(unittest.TestCase):
    def testReferenceSearcher(self):
        Globals.r_searcher = ReferenceSearcher(None)
        regions = []
        all_references = ReferenceList()

        all_references.append(Reference(60))

        r = MarkedRegion(50, 100)
        regions.append(r)
        Globals.r_searcher.search_all_pointers(regions, all_references)

        assert len(r.pointers) > 0, "PointerList of region is empty!"

if __name__ == "__main__":
    unittest.main()