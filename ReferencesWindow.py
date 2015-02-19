from PyQt5         import QtCore,QtGui,QtWidgets,uic
import Globals

RegionsUI = uic.loadUiType("references.ui")[0]

class ReferencesWindow(QtWidgets.QMainWindow,RegionsUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def referenceSelected(self,widget):
        self.parent.setPos(int(widget.text(),16))
        
    def show(self):
        self.lstRefs.clear()
        for r in Globals.hexGrid.allReferences:
            self.lstRefs.addItem("%08x" % r)
        super().show()
        self.activateWindow()
