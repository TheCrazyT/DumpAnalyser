from PropertiesWindow import *
from MarkedRegions    import *
from PyQt5            import QtCore, QtGui, QtWidgets, uic
import sys
import os

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    p      = PropertiesWindow()
    region = MarkedRegion(100,100)
    region.references.append(0x123456)
    p.show(region)
    sys.exit(app.exec_())
