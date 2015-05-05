from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals

ProgressUI = uic.loadUiType("progress.ui")[0]


class Progress(QtWidgets.QWidget, ProgressUI):
    def __init__(self, parent):
        super(Progress, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.parent = parent
        self.setupUi(self)
        self.on_stop = None

    def do_stop(self):
        if self.on_stop:
            self.on_stop()