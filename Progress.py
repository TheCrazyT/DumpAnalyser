from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
import Globals

ProgressUI = uic.loadUiType("progress.ui")[0]


class Progress(QtWidgets.QWidget, ProgressUI):
    value_changed = pyqtSignal(int)
    description_changed = pyqtSignal(str)
    maximum_changed = pyqtSignal(int)
    def __init__(self, parent):
        super(Progress, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.parent = parent
        self.setupUi(self)
        self.value_changed.connect(self.progressBar.setValue)
        self.maximum_changed.connect(self.progressBar.setMaximum)
        self.on_stop_signal = None
        self.description_changed.connect(self.lblDescription.setText)

    def do_stop(self):
        if self.on_stop_signal:
            self.on_stop_signal.emit()