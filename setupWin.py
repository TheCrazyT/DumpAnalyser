from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
includefiles = ["mywindow.ui","properties.ui","references.ui","regions.ui","rva_map.ui","search.ui","searchResults.ui","toolmenu.ui"]
buildOptions = dict(packages = [], excludes = [], include_files = includefiles)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('MainWindow.py', base=base, targetName = 'DumpAnalyser.exe')
]

setup(name='DumpAnalyser.exe',
      version = '1.0',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
