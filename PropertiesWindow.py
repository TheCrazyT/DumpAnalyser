from PyQt5         import QtCore,QtGui,QtWidgets,uic
import Globals

(TYPE_REF,TYPE_REFS) = range(0,2)
PropertiesUI = uic.loadUiType("properties.ui")[0]

class PropertiesWindow(QtWidgets.QMainWindow,PropertiesUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi(self)

    def gotoRef(self,item):
        print("gotoRef")
        pos = int(item.text(0),16)
        if(self.parent != None):
            Globals.mainWindow.setPos(pos)
            Globals.hexGrid.temp_select(pos,int(len(item.text(0))/2))

    def itemClick(self,item):
        if item.type == TYPE_REFS:
            self.gotoRef(item)
        if item.type == TYPE_REF:
            Globals.mainWindow.setPos(item.ref)

    def show(self,region):
        self.tvProps.clear()
        if region != None:
            tliRef = QtWidgets.QTreeWidgetItem()
            if region.virtualPos == None:
                Globals.rSearcher.calculateSearchDataByRva(region)
            tliRef.setText(0,"References of %08x (%08x)" % (region.startPos,region.virtualPos))
            for r in region.references:
                tli      = QtWidgets.QTreeWidgetItem()
                tli.type = TYPE_REFS
                tli.setText(0,"%08x" % r)
                tliRef.addChild(tli)
            self.tvProps.addTopLevelItem(tliRef)
            tliRef.setExpanded(True)
        if self.showRefs:
            tliRef = QtWidgets.QTreeWidgetItem()
            tliRef.setText(0,"Selected reference leads to %08x" % (self.ref,))
            tliRef.type = TYPE_REF
            tliRef.ref  = self.ref
            self.tvProps.addTopLevelItem(tliRef)
            tliRef.setExpanded(True)
            
        super().show()
        super().activateWindow()
