import sqlite3
from MarkedRegions import *

(TYPE_NULLSTRING,) = range(0, 1)

conn = None
cur = None


def connect(filename):
    global conn, cur
    conn = sqlite3.connect(filename)
    conn.text_factory = str
    cur = conn.cursor()


def commit():
    global conn
    conn.commit()


def close():
    global conn, cur
    cur.close()
    conn.close()


def load_region_properties(region_id):
    global cur
    properties = []
    try:
        cur.execute("SELECT type,startPos,endPos FROM regions_props WHERE regionId=?", (region_id,))
        rows = cur.fetchall()
        for row in rows:
            if row[0] == TYPE_NULLSTRING:
                nullstring = NullString(row[1])
                nullstring.end_pos = row[2]
                properties.append(nullstring)
    except sqlite3.OperationalError:
        pass
    return properties


def load_region_references(region_id):
    global cur
    references = ReferenceList()
    cur.execute("SELECT pos FROM regions_ref WHERE regionId=? GROUP BY pos", (region_id,))
    rows = cur.fetchall()
    for row in rows:
        references.append(Reference(row[0]))
    return references


def load_regions():
    global cur
    regions = RegionList()
    cur.execute("SELECT startPos,length,id,color,fullyScanned FROM regions")
    rows = cur.fetchall()
    for row in rows:
        r = MarkedRegion(row[0], row[1], row[2], row[3], row[4])
        regions.append(r)
        r.references.extend(load_region_references(row[2]))
        r.properties.extend(load_region_properties(row[2]))
    return regions


def save_region_properties(region):
    global cur
    for p in region.properties:
        if type(p) is NullString:
            cur.execute("INSERT INTO regions_props (type,startPos,endPos,regionId) VALUES (?,?,?,?)",
                        (0, p.start_pos, p.end_pos, region.id))


def save_region_refs(region):
    global cur
    for r in region.references:
        cur.execute("INSERT INTO regions_ref (regionId,pos) VALUES (?,?)", (region.id, r.addr))


def save_region(region):
    global cur
    save_region_refs(region)
    save_region_properties(region)
    cur.execute("INSERT INTO regions (id,startPos,length,color,fullyScanned) VALUES (?,?,?,?,?)",
                (region.id, region.start_pos, region.length, region.color, region.fully_scanned))


def create_rva_list_tbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS rvalist ( \
         "rva" INTEGER,\
         "virtoff" INTEGER,\
         "size" INTEGER\
         )')


def create_regions_tbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions ( \
         "id" INTEGER,\
         "startPos" INTEGER,\
         "length" INTEGER,\
         "color" VARCHAR,\
         "fullyScanned" INTEGER\
         )')


def create_regions_prop_tbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions_props ( \
         "type" INTEGER,\
         "startPos" INTEGER,\
         "endPos" INTEGER,\
         "regionId" INTEGER\
         )')


def create_regions_ref_tbl():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS regions_ref ( \
         "regionId" INTEGER,\
         "pos" INTEGER\
         )')


def save_rva_list(rva_list):
    db.cur.executemany('INSERT INTO rvalist (rva,virtoff,size) VALUES(?,?,?)', rva_list)


def load_rva_list():
    rvaList = []
    cur.execute("SELECT rva,virtoff,size FROM rvalist")
    rows = cur.fetchall()
    for row in rows:
        rvaList.append((row[0], row[1], row[2]))
    return rvaList
