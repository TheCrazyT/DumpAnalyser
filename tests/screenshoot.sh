#!/bin/bash

function fatal_error {
	kill $jXvfb
	kill $jpython3
	cd tests
	exit 1
}

export DISPLAY=:1
rm ../screenshoots/screen1.png 2>/dev/null
mkdir /tmp/X 2>/dev/null
Xvfb -fbdir /tmp/X -screen 0 1920x1080x24 :1 1>/dev/Xvfb_info.log 2>/dev/Xvfb_error.log &
if [ $? != 0 ]
then
	echo "Fatal error"
	cat Xvfb_info.log
	cat Xvfb_error.log
	exit 1
fi
jXvfb=$!
sleep 1
cd ..

python3 tests/screenshoot1.py &
jpython3=$!
sleep 3
xwd -root | convert -bordercolor black -border 1x1 -trim - screenshoots/screen1.png
sleep 3
if [ $? != 0 ]
then
	fatal_error
fi
kill $jpython3

#python3 tests/screenshoot2.py &
#jpython3=$!
#xwd -root | convert - screenshoots/screen1.png
#kill $jpython3

kill $jXvfb
cd tests
