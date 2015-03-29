tests: PropertiesWindowTest MarkableGridTest ReferenceSearcherTest

PropertiesWindowTest:
	PYTHONPATH=$(shell pwd) python tests/PropertiesWindowTest.py

MarkableGridTest:
	PYTHONPATH=$(shell pwd) python tests/MarkableGridTest.py

ReferenceSearcherTest:
	PYTHONPATH=$(shell pwd) python tests/ReferenceSearcherTest.py

SearchWindowTest:
	PYTHONPATH=$(shell pwd) python tests/SearchWindowTest.py

all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest