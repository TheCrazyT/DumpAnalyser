from PyQt5         import QtCore,QtGui,QtWidgets,uic
import Globals
from   Globals import *

(TYPE_REF,TYPE_REFS,TYPE_POINTER,TYPE_REGION) = range(0,4)
PropertiesUI = uic.loadUiType("properties.ui")[0]

class PropertiesWindow(QtWidgets.QMainWindow,PropertiesUI):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.parent   = parent
        self.showRefs = True
        self.ref      = 0

    def gotoRef(self,pos,ptrSize):
        dbg("gotoRef")
        if(self.parent != None):
            Globals.mainWindow.setPos(pos)
            Globals.hexGrid.temp_select(pos,ptrSize)

    def itemClick(self,item):
        if item.type == TYPE_REGION:
            Globals.mainWindow.setPos(item.data)
        if item.type == TYPE_REFS:
            self.gotoRef(item.data,4)
        if item.type == TYPE_REF:
            Globals.mainWindow.setPos(item.data)
        if item.type == TYPE_POINTER:
            Globals.mainWindow.setPos(item.data)

    def show(self,region):
        self.tvProps.clear()
        if region != None:
            tliRef = QtWidgets.QTreeWidgetItem()
            tliRef.data = region.startPos
            tliRef.type = TYPE_REGION
            if region.virtualPos == None:
                Globals.rSearcher.calculateSearchDataByRva(region)
            tliRef.setText(0,"References of %08x (%08x)" % (region.startPos,region.virtualPos))
            for r in region.references:
                tli      = QtWidgets.QTreeWidgetItem()
                tli.type = TYPE_REFS
                tli.data = r.addr
                tli.setText(0,"%08x" % r.addr)
                tliRef.addChild(tli)
            self.tvProps.addTopLevelItem(tliRef)
            tliRef.setExpanded(True)
            
            tliRef = QtWidgets.QTreeWidgetItem()
            tliRef.data = region.startPos
            tliRef.type = TYPE_REGION
            tliRef.setText(0,"Pointers of %08x (%08x)" % (region.startPos,region.virtualPos))
            for p in region.pointers:
                tli      = QtWidgets.QTreeWidgetItem()
                tli.type = TYPE_POINTER
                ref      = Globals.rSearcher.calculatePointerPosRVA(p.addr)
                if ref != None:
                    vpos     = Globals.rSearcher.calculateVirtByRVA(ref)
                    if vpos != None:
                        tli.setText(0,"+%08x to %08x (%08x)" % (p.addr-region.startPos,ref,vpos))
                        tli.data = ref
                        tliRef.addChild(tli)
            self.tvProps.addTopLevelItem(tliRef)
            tliRef.setExpanded(True)
            
        if self.showRefs:
            if self.ref:
                tliRef = QtWidgets.QTreeWidgetItem()
                vpos     = Globals.rSearcher.calculateVirtByRVA(self.ref)
                if vpos != None:
                    tliRef.setText(0,"Selected reference leads to %08x (%08x)" % (self.ref,vpos))
                    tliRef.type = TYPE_REF
                    tliRef.data = self.ref
                    self.tvProps.addTopLevelItem(tliRef)
                tliRef.setExpanded(True)
            
        super().show()
        super().activateWindow()
