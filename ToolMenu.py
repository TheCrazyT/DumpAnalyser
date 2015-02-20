from PyQt5 import QtCore, QtGui, QtWidgets
import Globals

class ToolMenu(QtWidgets.QVBoxLayout):
   def __init__(self,parent):
       QtWidgets.QVBoxLayout.__init__(self)
       self.setAlignment(QtCore.Qt.AlignTop)
       self.parent        = parent
       self.btnBlock      = QtWidgets.QPushButton("Region")
       self.btnNullString = QtWidgets.QPushButton("Null terminated string")
       self.btnString     = QtWidgets.QPushButton("Size limited string")
       self.btnBlock.setEnabled(False)
       self.btnNullString.setEnabled(False)
       self.btnString.setEnabled(False)
       
       self.btnBlock.clicked.connect(self.on_btnBlock_clicked)
       self.btnNullString.clicked.connect(self.on_btnNullString_clicked)
       self.btnString.clicked.connect(self.on_btnString_clicked)
       
       self.addWidget(self.btnBlock)
       self.addWidget(self.btnNullString)
       self.addWidget(self.btnString)

   def enableBlock(self):
       self.btnBlock.setEnabled(True)
       
   def disableBlock(self):
       self.btnBlock.setEnabled(False)

   def enableRegionButtons(self):
      self.btnNullString.setEnabled(True)
      self.btnString.setEnabled(True)
      
   def disableRegionButtons(self):
      self.btnNullString.setEnabled(False)
      self.btnString.setEnabled(False)

   def on_btnBlock_clicked(self,event):
      Globals.hexGrid.store_region()

   def on_btnNullString_clicked(self,event):
      Globals.hexGrid.store_nullstring()

   def on_btnString_clicked(self,event):
      Globals.hexGrid.store_string()
