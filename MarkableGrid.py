from PyQt5 import QtCore, QtGui, QtWidgets
from MarkedRegions    import *
import Globals

class MySelectionModel(QtCore.QItemSelectionModel):
   def __init__(self,model):
      QtCore.QItemSelectionModel.__init__(self,model)
      self.model = model
   def select(self,i,flags):
      width  = Globals.hexGrid.width
      height = Globals.hexGrid.height
      if type(i) is not QtCore.QModelIndex:
         if(flags & QtCore.QItemSelectionModel.Select):
            Globals.toolMenu.enableRegion()
            Globals.toolMenu.enableRegionButtons()
            maxIidx = None
            minIidx = None
            for k in i.indexes():
               if minIidx == None:
                  minIidx = k.row()*width+k.column()
               if maxIidx == None:
                  maxIidx = k.row()*width+k.column()
               idx = k.row()*width+k.column()
               if idx<minIidx:
                  minIidx = k.row()*width+k.column()
               if idx>maxIidx:
                  maxIidx = k.row()*width+k.column()
            i.clear()
            col1 = minIidx % width
            col2 = maxIidx % width
            row1 = int((minIidx-col1)/width)
            row2 = int((maxIidx-col2)/width)
            cIdx = self.currentIndex()
            if (cIdx.column()==col1):
               col1 = col2
               col2 = cIdx.column()
            if row1+2<=row2:
               idx1 = self.model.createIndex(row1+1,0)
               idx2 = self.model.createIndex(row2-1,width)
               sr   = QtCore.QItemSelectionRange(idx1,idx2)
               i.append(sr)
            if row1<row2:
               idx1 = self.model.createIndex(row1,col1)
               idx2 = self.model.createIndex(row1,width)
               sr   = QtCore.QItemSelectionRange(idx1,idx2)
               i.append(sr)
               idx1 = self.model.createIndex(row2,0)
               idx2 = self.model.createIndex(row2,col2)
               sr   = QtCore.QItemSelectionRange(idx1,idx2)
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
      if Globals.mainWindow.size == None:
         return 0
      if Globals.hexGrid.width == 0:
         return 0
      return int(Globals.mainWindow.fileSize/Globals.hexGrid.width)
   def columnCount(self, parent):
      return Globals.hexGrid.width+2
   def data(self, index, role):
      if role == QtCore.Qt.BackgroundRole:
         if index.column()!=0:
            if index.column()!=Globals.hexGrid.width+1:
               if Globals.hexGrid.text != None:
                  rect   = Globals.hexGrid.viewport().rect()
                  topRow = Globals.hexGrid.indexAt(rect.topLeft()).row()
                  x      = index.column()-1
                  y      = index.row()-topRow
                  try:
                     if Globals.hexGrid.text[x][y] != None:
                        c = Globals.hexGrid.text[x][y]
                        return QtGui.QBrush(c.color)
                  except(IndexError):
                     #print("data(%d,%d)" % (x,y))
                     pass
      if not index.isValid():
         return None
      elif role != QtCore.Qt.DisplayRole:
         return None
      if index.column()==Globals.hexGrid.width+1:
         return Globals.mainWindow.readTxt(index.row()*Globals.hexGrid.width,Globals.hexGrid.width)
      if index.column()==0:
         return "%08x" % (index.row()*Globals.hexGrid.width)
      return Globals.mainWindow.readHex(index.row()*Globals.hexGrid.width+index.column())
   def headerData(self, col, orientation, role):
      return None
   def canFetchMore(self,parent):
      print("canFetchMore")
      return True
   def fetchMore (self,parent):
      print("fetchMore")
      print(parent)
      return None
   def flags(self,index):
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

class MarkableGrid(QtWidgets.QTableView):
   def __init__(self,parent,width,height):
      Globals.hexGrid       = self
      QtWidgets.QTableView.__init__(self)
      self.parent           = parent
      self.verticalScrollBar().valueChanged.connect(self.onScroll)
      font  = QtGui.QFont("Monospace", 8);
      font.setStyleHint(QtGui.QFont.TypeWriter);
      self.setFont(font);
      self.regions       = MarkedRegions()
      self.allReferences = []
      self.viewRegions   = []
      self.width         = width
      self.height        = height
      self.text          = None

   def mousePressEvent(self,event):
      print("mousePressEvent")
      print(event)
      super().mousePressEvent(event)
      rect   = self.viewport().rect()
      index  = self.currentIndex()
      topRow = Globals.hexGrid.indexAt(rect.topLeft()).row()
      x      = index.column()-1
      y      = index.row()-topRow
      if self.text!=None:
         if self.text[x]!=None:
            if self.text[x][y]!=None:
               self.text[x][y].mousePressEvent(event)

   def updateView(self):
      rect             = self.viewport().rect()
      topRow           = self.indexAt(rect.topLeft()).row()
      self.viewRegions = []
      self.text        = []
      Globals.mainWindow.pos = topRow*Globals.hexGrid.width
      self.calc_view_regions(Globals.mainWindow.pos,Globals.mainWindow.pos+self.width*self.height)
      for x in range(0,self.width):
         i = []
         self.text.append(i)
         for y in range(0,self.height):
               i.append(None)
      for rl in self.viewRegions:
         for r in rl:
            (item,color) = r
            if color != None:
               item.setColor(color)
               self.text[item.x][item.y] = item

   def onScroll(self,*args):
      print("scrollTo")
      print(args)
      self.updateView()

   def update(self):
      i1 = QtCore.QModelIndex()
      i2 = QtCore.QModelIndex()
      self.dataChanged(i1,i2,[])
      self.model          = MyTableModel(self)
      self.selectionModel = MySelectionModel(self.model)
      self.setModel(self.model)
      self.setSelectionModel(self.selectionModel)

      MARGIN          = 8
      CHAR_WIDTH      = 7
      OFFSET_WIDTH    = MARGIN + CHAR_WIDTH * 8
      TEXT_WIDTH      = MARGIN + CHAR_WIDTH * self.width
      COL_WIDTH       = MARGIN + CHAR_WIDTH * 2
      SCROLLBAR_WIDTH = 8
      self.setColumnWidth(0,OFFSET_WIDTH)
      self.setColumnWidth(self.width+1,TEXT_WIDTH)
      for i in range(1,self.width+1):
         self.setColumnWidth(i,COL_WIDTH)
      for i in range(0,self.height):
         self.setRowHeight(i,24)
      self.setMinimumWidth(SCROLLBAR_WIDTH+OFFSET_WIDTH+TEXT_WIDTH+(self.width)*COL_WIDTH)
      self.setMinimumHeight((2+self.height)*24)
      self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      
   def load(self):
      self.regions.load()

   def save(self):
      self.regions.save()

   def reset_regions(self):
      self.regions     = MarkedRegions()
      self.viewRegions = []

   def calc_view_regions(self,startPos,endPos):
      print("calc_view_regions %08x,%08x" % (startPos,endPos))
      regionsInView = self.regions.findWithin(startPos,endPos)
      regionEntryList = []
      for r in regionsInView:
         for y in range(0,self.height):
            for x in range(0,self.width):
               i = Globals.mainWindow.pos + y*self.width + x
               if i>=r.startPos and i<=r.endPos:
                  regionEntryList.append((MarkableCell(self,x,y),r.get_color(i,Globals.mainWindow.readTxt(y*self.width+x,1))))
      for y in range(0,self.height):
         for x in range(0,self.width):
            if Globals.mainWindow.action_References.isChecked():
               i = Globals.mainWindow.pos + y*self.width + x
               for j in range(0,4):
                  if ((i-j) in self.allReferences):
                     regionEntryList.append((MarkableCell(self,x,y),QtGui.QColor(0x00FF00)))
         self.viewRegions.append(regionEntryList)
   
   def resize_region(self,region,newStartPos,newEndPos):
      print("resize_region %08x %08x" % (newStartPos,newEndPos) )
      if newStartPos!=region.startPos:
         for ref in region.references:
            self.allReferences.remove(ref)
         region.fullyScanned = False
      region.startPos = newStartPos
      region.endPos   = newEndPos
      region.references = []
      
   def merge_regions(self,regions,startPos,endPos):
      print("merge_regions")
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

   def get_start_end_sel(self):
      x2 = None
      y2 = None
      x1 = None
      y1 = None
      for x in self.selectedIndexes():
         if (x1==None) or (y1==None) or (x.row()<y1):
            y1 = x.row()
            x1 = x.column()
         elif (x2==None) or (x.row()==y1) and (x.column()<x1):
            x2 = x.column()
         if (x2==None) or (y2==None) or (x.row()>y2):
            y2 = x.row()
            x2 = x.column()
         elif (x2==None) or (x.row()==y2) and (x.column()>x2):
            x2 = x.column()
      print("get_start_end_sel %d %d - %d %d" % (x1,y1,x2,y2))
      startPos = (x1-1) + y1*self.width
      endPos   = (x2-1) + y2*self.width
      return (startPos,endPos)
   
   def store_region(self):

      (startPos,endPos) = self.get_start_end_sel()
      print("store_region %d-%d" % (startPos,endPos))
      (action,result) = self.detect_region_action(startPos,endPos)
      if   action == 0:
         self.new_region(startPos,endPos)
      elif action == 1:
         self.merge_regions(result,startPos,endPos)
      elif action == 2:
         self.resize_region(result,startPos,endPos)
      self.viewRegions = []
      self.updateView()
      self.selectionModel.clearSelection()

   def store_nullstring(self):
      print("store_nullstring")
      (startPos,endPos) = self.get_start_end_sel()
      regions      = self.regions.findWithin(startPos,endPos)
      print("len(regions): %d" % len(regions))
      if len(regions) != 1:
         print("%d region found" % len(regions))
         return
      r            = regions[0]
      r.add_nullstring(startPos)
      self.selectionModel.clearSelection()
 
   def store_string(self):
      (startPos,endPos) = self.get_start_end_sel()
      regions = self.regions.findWithin(startPos,endPos)
      self.selectionModel.clearSelection()
      if len(regions) != 1:
         return

   def delete_region(self,region):
      print("delete_region")
      for ref in region.references:
            self.allReferences.remove(ref)
      self.regions.remove(region)
      
   def erase(self):
      (startPos,endPos) = self.get_start_end_sel()
      print("erase %08x %08x" % (startPos,endPos))
      regions = self.regions.findWithin(startPos,endPos)
      self.selectionModel.clearSelection()
      if len(regions) != 1:
         print("%d region found" % len(regions))
         return
      region = regions[0]
      print("region %08x %08x" % (region.startPos,region.endPos))
      if (startPos <= region.startPos)and(endPos >= region.endPos):
         self.delete_region(region)
      else:
         if (startPos <= region.startPos)and(endPos < region.endPos):
            self.resize_region(region,endPos+1,region.endPos)
         elif (startPos > region.startPos)and(endPos >= region.endPos):
            self.resize_region(region,region.startPos,startPos-1)
      self.viewRegions = []
      self.updateView()
      self.selectionModel.clearSelection()

   def clear_selection(self):
      self.selectionModel.clearSelection()
      
   def temp_select(self,startPos,length):
      endPos       = startPos + length
      selectedItems = QtCore.QItemSelection()

      x1 = startPos % self.width
      y1 = int((startPos - x1) / self.width)
      x1 += 1

      x2 = endPos % self.width
      y2 = int((endPos - x2) / self.width)

      print("temp_select %d,%d - %d,%d" % (x1,y1,x2,y2))
      topLeft       = self.model.index(y1,x1,QtCore.QModelIndex())
      bottomRight   = self.model.index(y2,x2,QtCore.QModelIndex())
      selectedItems.select(topLeft,bottomRight)
      self.selectionModel.clearSelection()
      self.selectionModel.select(selectedItems, QtCore.QItemSelectionModel.Select)
      
class MarkableCell(QtWidgets.QWidget):
   def __init__(self,parent,x,y):
      super(MarkableCell,self).__init__()
      self.parent = parent
      self.x      = x
      self.y      = y
      self.color  = QtGui.QColor(0xFFFFFF)
      self.parent = parent

   def setColor(self,color):
      self.color = color

   def mousePressEvent(self,event):
      print("mousePressEvent")
      if (event.button()== QtCore.Qt.RightButton):
          reference = None
          startPos  = Globals.mainWindow.pos+self.y*Globals.hexGrid.width+self.x
          showRefs  = False
          for i in range(0,4):
             if startPos - i in Globals.hexGrid.allReferences:
                reference = Globals.rSearcher.calculatePointerPosRVA(startPos-i)
                showRefs  = True
          r = Globals.hexGrid.regions.findWithin(startPos,startPos)
          Globals.propertiesWindow.showRefs = showRefs
          Globals.propertiesWindow.ref      = reference
          if len(r)>0:
             Globals.propertiesWindow.show(r[0])
          else:
             if showRefs:
                Globals.propertiesWindow.show(None)
