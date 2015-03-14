tests: PropertiesWindowtTest MarkableGridTest

PropertiesWindowtTest:
	echo "Errors:" > /tmp/pythonerrors.log
	(sleep 60 ; if [[ -e /tmp/python.pid ]]; then kill $$(cat /tmp/python.pid) ; fi ; )&
	-(TESTFILE=tests/PropertiesWindowTest.py;PYTHONPATH=$(shell pwd) python $$TESTFILE 2>>/tmp/pythonerrors.log;rm /tmp/python.pid 2>/dev/null) & echo $$! >/tmp/python.pid && sleep 1 && if [[ -e /tmp/python.pid ]];then wait $$(cat /tmp/python.pid);fi;
	-rm /tmp/python.pid 2>/dev/null
	-ls -ls /tmp/pythonerrors.log|awk '{ print $$6 }'|erep ^8$$ > /dev/null || cat /tmp/pythonerrors.log
	
MarkableGridTest:
	echo "Errors:" > /tmp/pythonerrors.log
	(sleep 60 ; if [[ -e /tmp/python.pid ]]; then kill $$(cat /tmp/python.pid) ; fi ; )&
	-(TESTFILE=tests/MarkableGridTest.py;PYTHONPATH=$(shell pwd) python $$TESTFILE 2>>/tmp/pythonerrors.log;rm /tmp/python.pid 2>/dev/null) & echo $$! >/tmp/python.pid && sleep 1 && if [[ -e /tmp/python.pid ]];then wait $$(cat /tmp/python.pid);fi;
	-rm /tmp/python.pid 2>/dev/null
	-ls -ls /tmp/pythonerrors.log|awk '{ print $$6 }'|egrep ^8$$ > /dev/null || cat /tmp/pythonerrors.log
	
all:
	-rm -R build/exe.*
	python setupWin.py build

.PHONY: all tests PropertiesWindowtTest