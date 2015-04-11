tests: PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest

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

all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowTest MarkableGridTest ReferenceSearcherTest SearchWindowTest ReferenceListTest