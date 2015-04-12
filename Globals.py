from PyQt5.QtCore import QMutex, QMutexLocker
from PyQt5 import QtWidgets

r_searcher = None
hex_grid = None
main_window = None
regions_window = None
properties_window = None
tool_menu = None
references_window = None
search_window = None
DEBUG = False
SLEEP_BETWEEN_REGIONS = 1
SLEEP_BETWEEN_REGION_SCAN = 0.1
SLEEP_BETWEEN_REGION_READ = 1
DBG_MUTEX = QMutex()

pointer_size = 4

def dbg(s):
    if (DEBUG):
        with QMutexLocker(DBG_MUTEX):
            print(s)

def input(widget,txt,label):
    dialog = QtWidgets.QInputDialog()
    return dialog.getText(widget, txt, label, QtWidgets.QLineEdit.Normal, "")
