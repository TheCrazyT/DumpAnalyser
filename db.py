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
    dbg("loaded %d references for regionId %d" % (len(rows),region_id))
    for row in rows:
        references.append(Reference(row[0]))
    return references


def load_regions():
    global cur
    Globals.r_searcher.reset_ref_map()
    regions = RegionList()

    columns = MarkedRegion.__db_columns__()[0]
    column_list = ""
    for column in columns:
        column_list += "%s," % column
    if(len(column_list)>0):
        column_list = column_list[0:len(column_list)-1]

    cur.execute("SELECT startPos,length,id,fullyScanned,%s FROM regions" % column_list)
    rows = cur.fetchall()
    for row in rows:
        r = MarkedRegion(row[0], row[1], row[2])

        i = 4
        for column in columns:
            getattr(r, columns[column])(row[i])
            i+=1

        fully_scanned = row[3]
        ref = Globals.r_searcher.get_ref(r)
        ref.set_fully_scanned(fully_scanned)
        regions.append(r)
        r.references.extend(load_region_references(row[2]))
        r.properties.extend(load_region_properties(row[2]))
    return regions

def load_indexed_pages():
    global cur
    indexed_pages = []
    try:
        cur.execute("SELECT page,value FROM indexed_pages ORDER BY page ASC")
        rows = cur.fetchall()
        last_page = -1
        pg = set()
        indexed_pages.append(pg)
        for row in rows:
            page = row[0]
            value = row[1]
            if page!=last_page:
                pg = set()
                indexed_pages.append(pg)
            pg.add(value)
            last_page = page
    except(sqlite3.OperationalError):
        pass
    Globals.r_searcher.set_indexed_pages(indexed_pages)


def save_region_properties(region):
    global cur
    for p in region.properties:
        if type(p) is NullString:
            cur.execute("INSERT INTO regions_props (type,startPos,endPos,regionId) VALUES (?,?,?,?)",
                        (0, p.start_pos, p.end_pos, region.id))


def save_region_refs(region):
    global cur
    for r in region.references:
        cur.execute("INSERT INTO regions_ref (regionId,pos) VALUES (?,?)", (region.id, r.address))


def save_region(region):
    global cur
    save_region_refs(region)
    save_region_properties(region)
    ref = Globals.r_searcher.get_ref(region)
    params = []
    params.append(ref.get_fully_scanned())
    columns = MarkedRegion.__db_columns__()[1]
    column_list = ""
    needed_params = ""
    for column in columns:
        needed_params += ",?"
        column_list += ",%s" % column
        params.append(getattr(region, columns[column])())

    cur.execute("INSERT INTO regions (fullyScanned%s) VALUES (?%s)" % (column_list,needed_params),
                params)

def save_indexed_pages():
    global cur
    indexed_pages = Globals.r_searcher.get_indexed_pages()

    k = 0
    for p in indexed_pages:
        for v in p:
            cur.execute("INSERT INTO indexed_pages (page,value) VALUES (?,?)" , (k,v))
        k += 1

def create_indexed_pages():
    global cur
    cur.execute('CREATE TABLE IF NOT EXISTS indexed_pages ( \
         "page" INTEGER,\
         "value" INTEGER)')

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
         "name" VARCHAR,\
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
