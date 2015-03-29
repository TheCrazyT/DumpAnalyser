import sqlite3
from MarkedRegions import *

(TYPE_NULLSTRING,) = range(0,1)

conn = None
cur  = None
def connect(filename):
    global conn,cur
    conn = sqlite3.connect(filename)
    conn.text_factory = str
    cur = conn.cursor()

def commit():
    global conn
    conn.commit()

def close():
    global conn,cur
    cur.close()
    conn.close()

def loadRegionProperties(regionId):
    global cur
    properties = []
    cur.execute("SELECT type,startPos,endPos FROM regions_props WHERE regionId=?",(regionId,))
    rows = cur.fetchall()
    for row in rows:
        if row[0] == TYPE_NULLSTRING:
            nullstring = NullString(row[1])
            nullstring.endPos   = row[2]
            properties.append(nullstring)
    return properties

def loadRegionReferences(regionId):
    global cur
    references = ReferenceList()
    cur.execute("SELECT pos FROM regions_ref WHERE regionId=? GROUP BY pos",(regionId,))
    rows = cur.fetchall()
    for row in rows:
        references.append(Reference(row[0]))
    return references

def loadRegions():
    global cur
    regions = []
    cur.execute("SELECT startPos,length,id,color,fullyScanned FROM regions")
    rows = cur.fetchall()
    for row in rows:
        r = MarkedRegion(row[0],row[1],row[2],row[3],row[4])
        regions.append(r)
        r.references.extend(loadRegionReferences(row[2]))
        r.properties.extend(loadRegionProperties(row[2]))
    return regions

def saveRegionProperties(region):
    global cur
    for p in region.properties:
        if type(p) is NullString:
            cur.execute("INSERT INTO regions_props (type,startPos,endPos,regionId) VALUES (?,?,?,?)",(0,p.startPos,p.endPos,region.id))

def saveRegionRefs(region):
    global cur
    for r in region.references:
        cur.execute("INSERT INTO regions_ref (regionId,pos) VALUES (?,?)",(region.id,r.addr))

def saveRegion(region):
    global cur
    saveRegionRefs(region)
    saveRegionProperties(region)
    cur.execute("INSERT INTO regions (id,startPos,length,color,fullyScanned) VALUES (?,?,?,?,?)",(region.id,region.startPos,region.length,region.color,region.fullyScanned))

def createRvaListTbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS rvalist ( \
         "rva" INTEGER,\
         "virtoff" INTEGER,\
         "size" INTEGER\
         )')

def createRegionsTbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions ( \
         "id" INTEGER,\
         "startPos" INTEGER,\
         "length" INTEGER,\
         "color" VARCHAR,\
         "fullyScanned" INTEGER\
         )')

def createRegionsPropTbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions_props ( \
         "type" INTEGER,\
         "startPos" INTEGER,\
         "endPos" INTEGER,\
         "regionId" INTEGER\
         )')

def createRegionsRefTbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions_ref ( \
         "regionId" INTEGER,\
         "pos" INTEGER\
         )')

def saveRvaList(rvaList):
    db.cur.executemany('INSERT INTO rvalist (rva,virtoff,size) VALUES(?,?,?)',rvaList)

def loadRvaList():
    rvaList = []
    cur.execute("SELECT rva,virtoff,size FROM rvalist")
    rows = cur.fetchall()
    for row in rows:
        rvaList.append((row[0],row[1],row[2]))
    return rvaList
