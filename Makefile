tests: PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest dbTest RegionsWindowTest RegionListTest VersionCompatibilityTest

PropertiesWindowTest:
	python -m tests.PropertiesWindowTest

MarkableGridTest:
	python -m tests.MarkableGridTest

ReferenceSearcherTest:
	python -m tests.ReferenceSearcherTest

SearchWindowTest:
	python -m tests.SearchWindowTest

ReferenceListTest:
	python -m tests.ReferenceListTest

RegionListTest:
	python -m tests.RegionListTest

dbTest:
	python -m tests.dbTest

RegionsWindowTest:
	python -m tests.RegionsWindowTest

VersionCompatibilityTest:
	python -m tests.VersionCompatibilityTest

all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest dbTest RegionsWindowTest RegionListTest VersionCompatibilityTest