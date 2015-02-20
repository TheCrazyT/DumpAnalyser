from PyQt5 import QtCore, QtGui, QtWidgets, uic
import Globals

ToolMenuUI = uic.loadUiType("toolmenu.ui")[0]

class ToolMenu(QtWidgets.QWidget,ToolMenuUI):
   def __init__(self,parent):
       super(ToolMenu,self).__init__(parent)
       self.parent = parent
       self.setupUi(self)

   def enableRegion(self):
       self.btnRegion.setEnabled(True)
       
   def disableRegion(self):
       self.btnRegion.setEnabled(False)

   def enableRegionButtons(self):
      self.btnNullString.setEnabled(True)
      self.btnString.setEnabled(True)
      
   def disableRegionButtons(self):
      self.btnNullString.setEnabled(False)
      self.btnString.setEnabled(False)

   def btnRegion_clicked(self,event):
      Globals.hexGrid.store_region()

   def btnNullString_clicked(self,event):
      Globals.hexGrid.store_nullstring()

   def btnString_clicked(self,event):
      Globals.hexGrid.store_string()
