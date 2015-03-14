tests: PropertiesWindowtTest MarkableGridTest

PropertiesWindowtTest:
	echo "Errors:" > /tmp/pythonerrors.log
	PYTHONPATH=$(shell pwd) python tests/PropertiesWindowTest.py 2>>/tmp/pythonerrors.log & echo $$! >/tmp/python.pid
	sleep 1
	-@kill $$(cat /tmp/python.pid) 2>/dev/null
	rm /tmp/python.pid
	-ls -ls /tmp/pythonerrors.log|awk '{ print $$6 }'|erep ^8$$ > /dev/null || cat /tmp/pythonerrors.log

MarkableGridTest:
	echo "Errors:" > /tmp/pythonerrors.log
	PYTHONPATH=$(shell pwd) python tests/MarkableGridTest.py 2>>/tmp/pythonerrors.log & echo $$! >/tmp/python.pid
	sleep 5
	-@kill $$(cat /tmp/python.pid) 2>/dev/null
	rm /tmp/python.pid
	-ls -ls /tmp/pythonerrors.log|awk '{ print $$6 }'|egrep ^8$$ > /dev/null || cat /tmp/pythonerrors.log
	
all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowtTest