import zipfile
from os import walk

f = []
for (dirpath, dirnames, filenames) in walk("."):
    f.extend(filenames)
    break

myZipFile = zipfile.ZipFile("dumpAnalyser_any.zip", "w")
for fn in f:
    if fn.endswith(".py") or fn.endswith(".bat") or fn.endswith(".ui"):
        myZipFile.write(fn, fn, zipfile.ZIP_DEFLATED)

