#!/usr/bin/env python
import sys
sys.path.insert(2, '/DumpAnalyser')
from MainWindow import *

class TestMainWindow(MainWindow):
   def __init__(self):
       MainWindow.__init__(self)
       #self.open_file("test.dmp")
       #Globals.hexGrid.clear_colors(True)

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
