from PyQt5 import QtCore, QtGui, QtWidgets
from MarkedRegions    import *
import Globals

class MySelectionModel(QtCore.QItemSelectionModel):
   def __init__(self,model):
      QtCore.QItemSelectionModel.__init__(self,model)
      self.model = model
   def select(self,i,flags):
      #if(flags & QtCore.QItemSelectionModel.Select):
      #   if(not self.hasSelection()):
      #      self.minSel = idx
      #if i is QtCore.QItemSelection:
      if type(i) is not QtCore.QModelIndex:
         if(flags & QtCore.QItemSelectionModel.Select):
            minI = None
            maxI = None
            for k in i.indexes():
               if minI == None:
                  minI = k
               if maxI == None:
                  maxI = k
               width  = Globals.hexGrid.width
               height = Globals.hexGrid.height
               q = maxI.row()*width+maxI.column()
               v = minI.row()*width+minI.column()
               w = k.row()*width+k.column()
               if w<v:
                  minI = k
               if w>q:
                  maxI = k
            v = minI.row()*width+minI.column()
            q = maxI.row()*width+maxI.column()
            c1   = v % width
            r1   = int((v-c1)/width)
            c2   = q % width
            r2  = int((q-c2)/width)
            if r1+2<=r2:
               idx1 = self.model.createIndex(r1+1,0)
               idx2 = self.model.createIndex(r2-1,width)
               sr  = QtCore.QItemSelectionRange(idx1,idx2)
               i.append(sr)
            if r1<r2:
               idx1 = self.model.createIndex(r1,c1)
               idx2 = self.model.createIndex(r1,width)
               sr = QtCore.QItemSelectionRange(idx1,idx2)
               i.append(sr)
            if r1<r2:
               idx1 = self.model.createIndex(r2,0)
               idx2 = self.model.createIndex(r2,c2)
               sr = QtCore.QItemSelectionRange(idx1,idx2)
               i.append(sr)
      super().select(i,flags)

      
class MyTableModel(QtCore.QAbstractTableModel):
   def __init__(self, parent, *args):
      QtCore.QAbstractTableModel.__init__(self, parent, *args)
   def supportedDragActions(self):
      return QtCore.Qt.MoveAction
   def supportedDropActions(self):
      return QtCore.Qt.MoveAction
   def rowCount(self, parent):
      return Globals.hexGrid.height
   def columnCount(self, parent):
      return Globals.hexGrid.width+2
   def data(self, index, role):
      if role == QtCore.Qt.BackgroundRole:
         if index.column()!=0:
            if index.column()!=Globals.hexGrid.width+1:
                  return QtGui.QBrush(Globals.hexGrid.text[index.row()][index.column()-1].color)
      if not index.isValid():
         return None
      elif role != QtCore.Qt.DisplayRole:
         return None
      if index.column()==Globals.hexGrid.width+1:
         return Globals.hexGrid.longedit[index.row()].text()
      if index.column()==0:
         return Globals.hexGrid.offsets[index.row()].text()
      return Globals.hexGrid.text[index.row()][index.column()-1].getText()
   def headerData(self, col, orientation, role):
      return None
   def flags(self,index):
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

class SimpleData():
      def __init__(self):
         self._text = None
      def setText(self,text):
         self._text = text
      def text(self):
         return self._text
      
class MarkableGrid(QtWidgets.QTableView):
   def __init__(self,parent,width,height):
      Globals.hexGrid       = self
      QtWidgets.QTableView.__init__(self)
      self.parent           = parent

      font  = QtGui.QFont("Monospace", 8);
      font.setStyleHint(QtGui.QFont.TypeWriter);
      self.setFont(font);
      #self.setSelectionMode (QtWidgets.QAbstractItemView.NoSelection)
      #self.setHorizontalSpacing(2)
      #self.setVerticalSpacing(2)
      self.text          = []
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
         #entry = QtWidgets.QLineEdit()
         entry = SimpleData()
         #font  = QtGui.QFont("Monospace", 8);
         #font.setStyleHint(QtGui.QFont.TypeWriter);
         #entry.setFont(font);
         #entry.setMaxLength(8)
         #entry.setFixedWidth(8*8)
         self.offsets.append(entry)
         #entry.setReadOnly(True)
         entry.setText("00000000")
         #self.addWidget(entry,y,0,1,1)
         for x in range(0,self.width):
            entry = MarkableCell(self,x,y)
            self.text[y].append(entry)
            #self.addLayout(entry,y,x+1)
         entry = SimpleData()
         #entry.setFixedWidth(width*8)
         #entry.setFont(font);
         #entry.setMaxLength(self.width)
         self.longedit.append(entry)
         #entry.setReadOnly(False)
         lastEntry = entry
         #self.addWidget(entry,y,width+2,1,width)
      self.model = MyTableModel(self)
      self.setModel(self.model)
      self.setSelectionModel(MySelectionModel(self.model))
      OFFSET_WIDTH = 70
      TEXT_WIDTH   = 160
      COL_WIDTH    = 25
      self.setColumnWidth(0,OFFSET_WIDTH)
      self.setColumnWidth(width+2,TEXT_WIDTH)
      for i in range(1,width+1):
         self.setColumnWidth(i,COL_WIDTH)
      for i in range(0,height):
         self.setRowHeight(i,24)
      self.setMinimumWidth(OFFSET_WIDTH+TEXT_WIDTH+(width)*COL_WIDTH)
      self.setMinimumHeight((2+height)*24)
      self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
   def update(self):
      i1 = QtCore.QModelIndex()
      i2 = QtCore.QModelIndex()
      self.dataChanged(i1,i2,[])
      #self.layoutChanged()
      
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
      regionEntryList = []
      for r in regionsInView:
         for y in range(0,self.height):
            for x in range(0,self.width):
               i = Globals.mainWindow.pos + y*self.width + x
               if i>=r.startPos and i<=r.endPos:
                  regionEntryList.append((self.text[y][x],r.get_color(i,Globals.mainWindow.buf[y*self.width+x])))
      for y in range(0,self.height):
         for x in range(0,self.width):
            if Globals.mainWindow.action_References.isChecked():
               i = Globals.mainWindow.pos + y*self.width + x
               for j in range(0,4):
                  if ((i-j) in self.allReferences):
                     regionEntryList.append((self.text[y][x],QtGui.QColor(0x00FF00)))
         self.viewRegions.append(regionEntryList)
   
   def clear_colors(self,all=False):
      print("clear colors")
      for r in self.text:
         for c in r:
            c.setColor(QtGui.QColor(0xFFFFFF))
      self.viewRegions = []
      self.calc_view_regions(Globals.mainWindow.pos,Globals.mainWindow.pos+self.width*self.height)
      for rl in self.viewRegions:
         for r in rl:
            (item,color) = r
            if color != None:
               item.setColor(color)
      print("clear colors end")


   def resize_region(self,region,newStartPos,newEndPos):
      if newStartpos!=region.startPos:
         for ref in region.references:
            Globals.hexGrid.allReferences.remove(ref)
         region.fullyScanned = False
      region.startPos  = newStartPos
      region.newEndpos = newEndPos
      region.references = []
      
   def merge_regions(self,regions,startPos,endPos):
      startPoses = []
      endPoses   = []
      startPoses.append(startPos)
      endPoses.append(endPos)
      for r in regions:
         startPoses.append(r.startPos)
         endPoses.append(r.endPos)
      startPos  = min(startPoses)
      endPos    = max(endPoses)
      newRegion = MarkedRegion(startPos,endPos-startPos)
      for r in regions:
         newRegion.properties.extend(r.properties)
      for r in regions:
         self.regions.remove(r)
      self.regions.append(newRegion)
      
   def new_region(self,startPos,endPos):
      print("%d,%d" % (startPos,endPos))
      r            = MarkedRegion(startPos,endPos-startPos)
      self.regions.add(r)


   def detect_region_action(self,startPos,endPos):
      (NEW_REGION,MERGE_REGIONS,RESIZE_REGION)=range(0,3)
      regions = self.regions.findWithin(startPos,endPos)
      if(len(regions)==0):
         print("NEW_REGION")
         return (NEW_REGION,None)
      elif(len(regions)>1):
         print("MERGE_REGION")
         return (MERGE_REGIONS,regions)
      elif(len(regions)==1):
         print("RESIZE_REGION")
         return (RESIZE_REGION,regions[0])
      
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
      (action,result) = self.detect_region_action(startPos,endPos)
      if   action == 0:
         self.new_region(startPos,endPos)
      elif action == 1:
         self.merge_regions(result,startPos,endPos)
      elif action == 2:
         self.resize_region(result,startPos,endPos)
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
      
class MarkableCell(QtWidgets.QWidget):
   def __init__(self,parent,x,y):
      super(MarkableCell,self).__init__()
      self.parent = parent
      self.x      = x
      self.y      = y
      self.color  = QtGui.QColor(0xFFFFFF)
      font        = QtGui.QFont("Monospace", 8);
      font.setStyleHint(QtGui.QFont.TypeWriter);
      self.parent              = parent
      self.tempSelect          = False
      self.text                = None

   def setColor(self,color):
      self.color = color

   def temp_select(self):
      self.tempSelect = True
      #self.lbl.font().setUnderline(True)
      #self.lbl.setStyleSheet("color:red;")
   
   def mousePressEvent(self,event):
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

   def setText(self,str):
      #if(self.tempSelect):
         #self.tempSelect = False
         #self.lbl.font().setUnderline(False)
         #self.lbl.setStyleSheet("background-color:white;")
      self.text = str

   def getText(self):
      return self.text
