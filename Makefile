tests: PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest dbTest RegionsWindowTest RegionListTest VersionCompatibilityTest

PropertiesWindowTest:
	PYTHONPATH=$(shell pwd) python tests/PropertiesWindowTest.py

MarkableGridTest:
	PYTHONPATH=$(shell pwd) python tests/MarkableGridTest.py

ReferenceSearcherTest:
	PYTHONPATH=$(shell pwd) python tests/ReferenceSearcherTest.py

SearchWindowTest:
	PYTHONPATH=$(shell pwd) python tests/SearchWindowTest.py

ReferenceListTest:
	PYTHONPATH=$(shell pwd) python tests/ReferenceListTest.py

RegionListTest:
	PYTHONPATH=$(shell pwd) python tests/RegionListTest.py

dbTest:
	PYTHONPATH=$(shell pwd) python tests/dbTest.py

RegionsWindowTest:
	PYTHONPATH=$(shell pwd) python tests/RegionsWindowTest.py

VersionCompatibilityTest:
	PYTHONPATH=$(shell pwd) python tests/VersionCompatibilityTest.py

all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest dbTest RegionsWindowTest RegionListTest VersionCompatibilityTest