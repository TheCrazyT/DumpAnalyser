#Usage:
# ## building can take some time ... ##
#img=$(docker build .)
#docker tag $img dump_analyser:screenshoot
#
#to create screenshoots from tests:
#./dockerScreenshoot.sh
FROM ubuntu
RUN apt-get update
RUN apt-get install -y wget make build-essential g++ qt5-default qt5-qmake python3 python3-dev imagemagick x11-utils Xvfb dbus netpbm
RUN wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4/PyQt-gpl-5.4.tar.gz -O /tmp/pyqt.tar.gz
RUN wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.5/sip-4.16.5.tar.gz -O /tmp/sip.tar.gz
RUN tar -C /tmp -xf /tmp/pyqt.tar.gz
RUN tar -C /tmp -xf /tmp/sip.tar.gz
RUN echo build sip;cd /tmp/sip-4.16.5;python3 configure.py;make install
RUN echo build pyqt;cd /tmp/PyQt-gpl-5.4;echo yes|python3 configure.py >/dev/null;make install
RUN rm -R /tmp/sip-4.16.5
RUN rm -R /tmp/PyQt-gpl-5.4
RUN apt-get remove python3-sip
ENV TERM=xterm-color
CMD=["cd /DumpAnalyser/tests/;./screenshoot.sh"]
