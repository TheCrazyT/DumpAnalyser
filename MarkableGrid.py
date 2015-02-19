from PyQt5 import QtCore, QtGui, QtWidgets
from MarkedRegions    import *
import Globals

class MarkableGrid(QtWidgets.QGridLayout):
   def __init__(self,parent,width,height):
      QtWidgets.QGridLayout.__init__(self)
      self.parent           = parent

      
      self.setHorizontalSpacing(2)
      self.setVerticalSpacing(2)
      self.text          = []
      self.colored       = []
      self.longedit      = []
      self.offsets       = []
      self.regions       = MarkedRegions()
      self.allReferences = []
      self.viewRegions   = []
      self.width         = width
      self.height        = height
      lastEntry          = None
      for y in range(0,self.height):
         self.text.append([])
         entry = QtWidgets.QLineEdit()
         font  = QtGui.QFont("Monospace", 8);
         font.setStyleHint(QtGui.QFont.TypeWriter);
         entry.setFont(font);
         entry.setMaxLength(8)
         entry.setFixedWidth(8*8)
         self.offsets.append(entry)
         entry.setReadOnly(True)
         entry.setText("00000000")
         self.addWidget(entry,y,0,1,1)
         for x in range(0,self.width):
            entry = MarkableCell(self,x,y)
            self.text[y].append(entry)
            self.addLayout(entry,y,x+1)
         entry = QtWidgets.QLineEdit()
         entry.setFixedWidth(width*8)
         entry.setFont(font);
         entry.setMaxLength(self.width)
         self.longedit.append(entry)
         entry.setReadOnly(False)
         lastEntry = entry
         self.addWidget(entry,y,width+2,1,width)

   def load(self):
      self.regions.load()

   def save(self):
      self.regions.save()

   def reset_regions(self):
      self.regions     = MarkedRegions()
      self.viewRegions = []

   def calc_view_regions(self,startPos,endPos):
      print("calc_view_regions %d,%d" % (startPos,endPos))
      regionsInView = self.regions.findWithin(startPos,endPos)
      for r in regionsInView:
         regionEntryList = []
         for y in range(0,self.height):
            for x in range(0,self.width):
               i = Globals.mainWindow.pos + y*self.width + x
               if i>=r.startPos and i<=r.endPos:
                  regionEntryList.append((self.text[y][x],r.get_color(i,Globals.mainWindow.buf[y*self.width+x])))
               if Globals.mainWindow.action_References.isChecked():
                  for j in range(0,4):
                     if ((i-j) in self.allReferences):
                        regionEntryList.append((self.text[y][x],"green"))
         self.viewRegions.append(regionEntryList)
   
   def clear_colors(self,all=False):
      print("clear colors")
      if all:
         for l in self.text:
            for c in l:
               c.lbl.setStyleSheet("background-color:white;")
         self.viewRegions   = []
         print(self.width)
         print(Globals.mainWindow.pos)
         self.calc_view_regions(Globals.mainWindow.pos,Globals.mainWindow.pos+self.width*self.height)
         for rl in self.viewRegions:
            for r in rl:
               (item,color) = r
               if color != None:
                  item.lbl.setStyleSheet("background-color:%s;" % color)
         return
      if len(self.colored)>0:
         for c in self.colored:
            c.lbl.setStyleSheet("background-color:white;")
         self.colored = []
      for rl in self.viewRegions:
         for r in rl:
            (item,color) = r
            if color != None:
               item.lbl.setStyleSheet("background-color:%s;" % color)
      Globals.toolMenu.disableBlock()
      print("clear colors end")

   def store_region(self):
      startPos = self.width*self.height + 1
      endPos   = 0
      for c in self.colored:
         i = c.y*self.width + c.x
         if startPos >= i:
            startPos = i
         if endPos   <= i:
            endPos   = i
      startPos    += Globals.mainWindow.pos
      endPos      += Globals.mainWindow.pos
      print("%d,%d" % (startPos,endPos))
      r            = MarkedRegion(startPos,endPos-startPos)
      self.regions.add(r)
      self.calc_view_regions(Globals.mainWindow.pos,Globals.mainWindow.pos+self.width*self.height)
      self.clear_colors()

   def store_nullstring(self):
      print("store_nullstring")
      startPos = self.width*self.height + 1
      endPos   = 0
      for c in self.colored:
         i = c.y*self.width + c.x
         if startPos >= i:
            startPos = i
         if endPos   <= i:
            endPos   = i
      startPos    += Globals.mainWindow.pos
      endPos      += Globals.mainWindow.pos
      regions      = self.regions.findWithin(startPos,endPos)
      print("len(regions): %d" % len(regions))
      if len(regions) != 1:
         return
      r            = regions[0]
      r.add_nullstring(startPos)
      self.clear_colors(True)
 
   def store_string(self):
      startPos = self.width*self.height + 1
      endPos   = 0
      for c in self.colored:
         i = c.y*self.width + c.x
         if startPos >= i:
            startPos = i
         if endPos   <= i:
            endPos   = i
      startPos    += Globals.mainWindow.pos
      endPos      += Globals.mainWindow.pos
      regions = self.regions.findWithin(startPos,endPos)
      if len(regions) != 1:
         return

   def temp_select(self,startPos,length):
      rStartPos = startPos - Globals.mainWindow.pos
      #oldy      = None
      #oldx      = None
      for i in range(rStartPos,rStartPos + length):
         px = i % self.width
         py = int((i-px) / self.width)
         #if oldy == None:
         #   oldy = py
         #if oldx == None:
         #   oldx = px
         try:
            self.text[py][px].temp_select()
         except(IndexError):
            print("INDEX ERROR for py: %s and px: %s" % (py,px))
            raise(BaseException())
         #if (oldy != py) or (i == rStartPos + length - 1):
         #   if px == 0:
         #      llen = oldx-self.width
         #   else:
         #      llen = px
         #   self.longedit[oldy].setSelection(oldx,llen)
         #   print("longedit selection(%d) %d %d" % (py,oldx,llen))
         #else:
         #   oldx = px
      
class MarkableCell(QtWidgets.QGridLayout):
   def __init__(self,parent,x,y):
      super(MarkableCell,self).__init__()
      self.parent = parent
      self.x      = x
      self.y      = y
      self.lbl    = QtWidgets.QLabel('00')
      self.lbl.setAcceptDrops(True)
      font        = QtGui.QFont("Monospace", 8);
      font.setStyleHint(QtGui.QFont.TypeWriter);
      self.lbl.setFont(font);
      self.addWidget(self.lbl)
      self.parent              = parent
      self.tempSelect          = False
      self.drag                = self.createDrag()
      self.lbl.mousePressEvent = self.on_mousePressEvent
      self.lbl.dragEnterEvent  = self.on_dragEnterEvent

   def createDrag(self):
      drag        = QtGui.QDrag(self)
      mimeData    = QtCore.QMimeData()
      mimeData.setText('%d.%d' % (self.x, self.y))
      drag.setMimeData(mimeData)
      pixmap      = self.lbl.grab()
      painter     = QtGui.QPainter(pixmap)
      painter.setCompositionMode(painter.CompositionMode_DestinationIn)
      painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
      painter.end()
      drag.setPixmap(pixmap)
      return drag
   
   def temp_select(self):
      self.tempSelect = True
      self.lbl.font().setUnderline(True)
      self.lbl.setStyleSheet("color:red;")
   
   def on_mousePressEvent(self,event):
      print("mousePressEvent")
      if (event.button()== QtCore.Qt.RightButton):
          reference = None
          startPos  = Globals.mainWindow.pos+self.y*Globals.hexGrid.width+self.x
          showRefs  = False
          for i in range(0,4):
             if startPos - i in Globals.hexGrid.allReferences:
                reference = Globals.rSearcher.calculatePointerPosRVA(startPos-i-Globals.mainWindow.pos)
                showRefs  = True
          r = Globals.hexGrid.regions.findWithin(startPos,startPos)
          Globals.propertiesWindow.showRefs = showRefs
          Globals.propertiesWindow.ref      = reference
          if len(r)>0:
             Globals.propertiesWindow.show(r[0])
          else:
             if showRefs:
                Globals.propertiesWindow.show(None)
          Globals.hexGrid.clear_colors()
      else:
          self.drag.exec()
          self.drag = self.createDrag()

   def on_dragEnterEvent(self,event):
      print("dragEnterEvent")
      event.accept()
      uid = event.mimeData().text()
      print("uid %s" % uid)
      (a,b) = uid.split(".")
      source = Globals.hexGrid.text[int(b)][int(a)]
      widget = self
      x1 = source.x
      y1 = source.y
      x2 = widget.x
      y2 = widget.y
      if (x2 != None)and(y1 != None):
         newcolored = []
         i1 = y1*Globals.hexGrid.width+x1
         i2 = y2*Globals.hexGrid.width+x2
         for i in range(i1,i2+1):
            x = i % Globals.hexGrid.width
            y = int((i-x) / Globals.hexGrid.width)
            if Globals.hexGrid.text[y][x] in Globals.hexGrid.colored:
               Globals.hexGrid.colored.remove(Globals.hexGrid.text[y][x])
            newcolored.append(Globals.hexGrid.text[y][x])
         Globals.hexGrid.clear_colors()
         for c in newcolored:
            c.lbl.setStyleSheet("background-color:blue;color:white;")
         Globals.hexGrid.colored = newcolored
      startPos  = Globals.mainWindow.pos+y1*Globals.hexGrid.width+x1
      endPos    = Globals.mainWindow.pos+y2*Globals.hexGrid.width+x2
      if len(Globals.hexGrid.regions.findWithin(startPos,endPos))>0:
         Globals.toolMenu.enableRegionButtons() 
      else:
         Globals.toolMenu.disableRegionButtons() 
      Globals.toolMenu.enableBlock() 

   def setText(self,str):
      if(self.tempSelect):
         self.tempSelect = False
         self.lbl.font().setUnderline(False)
         self.lbl.setStyleSheet("background-color:white;")
      self.lbl.setText(str)
