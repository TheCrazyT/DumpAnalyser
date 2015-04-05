from PyQt5.QtCore import QMutex, QMutexLocker

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

def dbg(s):
    if (DEBUG):
        with QMutexLocker(DBG_MUTEX):
            print(s)
