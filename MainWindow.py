#!/usr/bin/env python
import sys
import os
import db
import time
import string
import Globals
from   Globals import *
from struct            import *
from PyQt5             import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore      import QMutex, QMutexLocker
from MarkableGrid      import *
from ToolMenu          import *

from RegionsWindow     import *
from ReferencesWindow  import *
from RvaWindow         import *
from SearchWindow      import *
from PropertiesWindow  import *


from ReferenceSearcher import *
from CachedReader      import *

MainWindowUI = uic.loadUiType("mywindow.ui")[0]
      
class MainWindow(QtWidgets.QMainWindow,MainWindowUI):
   def delete_event(self, widget, event, data=None):
       return False

   def quitWindow(self):
      sys.exit(0)

   # Another callback
   def destroy(self, widget, data=None):
      self.rSearcher.stop()
      self.rSearcher.destroy()
      if(self.opened_file != None):
         self.opened_file.close()

   def showRegionsWindow(self):
      Globals.regionsWindow.show()

   def showRVAWindow(self):
      Globals.rvaWindow.show()

   def showSearchWindow(self):
      Globals.searchWindow.show(self.opened_file,self.fileSize,self.search)

   def showReferencesWindow(self):
      Globals.referencesWindow.show()

   def refreshReferences(self):
      self.statusBar().showMessage('Recalculating all references')
      Globals.hexGrid.allReferences = []
      for r in Globals.hexGrid.regions.regionList:
         r.references   = []
         r.fullyScanned = False
      tmpSBRR = Globals.SLEEP_BETWEEN_REGION_READ
      tmpSBRS = Globals.SLEEP_BETWEEN_REGION_SCAN
      tmpSBR  = Globals.SLEEP_BETWEEN_REGIONS
      Globals.SLEEP_BETWEEN_REGION_READ = 0
      Globals.SLEEP_BETWEEN_REGION_SCAN = 0
      Globals.SLEEP_BETWEEN_REGIONS     = 0
      Globals.rSearcher.forceScan       = True
      time.sleep(11)
      with QMutexLocker(Globals.rSearcher.lock):
         time.sleep(1)
      Globals.SLEEP_BETWEEN_REGION_READ = tmpSBRR
      Globals.SLEEP_BETWEEN_REGION_SCAN = tmpSBRS
      Globals.SLEEP_BETWEEN_REGIONS     = tmpSBR

   def search(self,pos):
      self.setPos(pos)
      Globals.hexGrid.temp_select(pos,len(Globals.searchWindow.txtSearch.text()))
      Globals.hexGrid.setFocus()

   def doLoad(self,filename):
         db.connect(filename)
         self.rvaList = db.loadRvaList()
         Globals.hexGrid.load()
         db.close()

   def load(self):
      (filename,unknown) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','./save','*.sav')
      if filename!= "":
         try:
            filename.index(".sav")
         except:
            filename = "%s.sav" % filename
         self.doLoad(filename)

   def goto(self):
      pos = 0
      (posStr,ok) = QtWidgets.QInputDialog.getText(self, "Position",
        "Enter position in hex:")
      if ok:
         pos = int(str(posStr),16)
         self.setPos(pos)
      
   def save(self):
      (filename,unknown) = QtWidgets.QFileDialog.getSaveFileName(self, 'save file','./save','*.sav')
      if filename!= "":
         try:
            filename.index(".sav")
         except:
            filename = "%s.sav" % filename
         try:
            os.remove(filename)
         except(FileNotFoundError):
            pass
         db.connect(filename)
         db.createRvaListTbl()
         db.createRegionsTbl()
         db.createRegionsRefTbl()
         db.createRegionsPropTbl()
         db.saveRvaList(self.rvaList)
         Globals.hexGrid.save()
         db.commit()
         db.close()
      
   def searchNext(self):
      pos      = Globals.searchWindow.searchNext()
      if pos == -1:
         return
      realPos  = pos
      pos     -= pos % Globals.hexGrid.width
      self.setPos(pos)
      Globals.hexGrid.temp_select(realPos,len(Globals.searchWindow.txtSearch.text()))
      Globals.hexGrid.setFocus()

   def setPos(self,pos):
      pos      -= pos % Globals.hexGrid.width
      self.pos  = pos
      y         = int(self.pos/Globals.hexGrid.width)
      idx       = Globals.hexGrid.model.index(y,0,QtCore.QModelIndex())
      Globals.hexGrid.scrollTo(idx)

   def readTxt(self,pos,length):
      self.cached_file.seek(pos)
      s  = self.cached_file.read(length)
      txt = ""
      for b in s:
         if (10 == b)or(13 == b)or(9 == b)or(chr(b) not in string.printable):
            txt += "."
         else:
            txt += chr(b)

      return txt

   def readPointer(self,pos):
      self.cached_file.seek(pos)
      b = self.cached_file.read(4)
      return b

   def readHex(self,pos):
      self.cached_file.seek(pos)
      b = self.cached_file.read(1)[0]
      return "%02x" % b

   def open_file(self,fname):
      self.opened_file = open(fname,"rb")
      self.opened_file.locker = None
      self.cached_file = CachedReader(self.opened_file)
      self.pos         = 0
      self.fileSize    = os.path.getsize(fname)
      Globals.hexGrid.update()
      Globals.rSearcher.file = CachedReader(self.opened_file)
      Globals.rSearcher.size = self.fileSize

   def open_dlg(self):
      if(self.opened_file != None):
         self.opened_file.close()
      (filename,unknown) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open dump file','.','')
      if filename!= "":
         self.open_file(filename)
      
   def __init__(self, parent=None):
       QtWidgets.QMainWindow.__init__(self, parent)
       Globals.mainWindow   = self
       
       self.rvaList      = []
       self.cachePos     = None
       self.cacheSize    = None
       self.cache        = None
       self.pos          = 0
       self.fileSize     = 0

       Globals.rSearcher    = ReferenceSearcher(self)
       Globals.hexGrid      = MarkableGrid(self,32,32)
       Globals.toolMenu     = ToolMenu(self)

       Globals.rvaWindow        = RvaWindow(self)
       Globals.searchWindow     = SearchWindow(self)
       Globals.regionsWindow    = RegionsWindow(self)
       Globals.referencesWindow = ReferencesWindow(self)
       Globals.propertiesWindow = PropertiesWindow(self)
       
       Globals.rSearcher.start()

       mainLayout = QtWidgets.QHBoxLayout()
       mainWidget = QtWidgets.QWidget()
       mainWidget.setLayout(mainLayout)
       mainLayout.addWidget(Globals.hexGrid)
       mainLayout.addWidget(Globals.toolMenu)
       
       self.setupUi(self)
       self.setCentralWidget(mainWidget)
       
       self.opened_file      = None
       self.statusBar().showMessage('Ready')

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
