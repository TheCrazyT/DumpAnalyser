import tempfile
import sys
import os
import shutil
from PyQt5 import QtWidgets
import unittest

class VersionCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.module_names = []
        self.dir = tempfile.mkdtemp()
        self.main_dir = os.getcwd()

        p = os.popen("git tag -l")
        tags_str = "%s" % p.read()
        p.close()
        tags = tags_str.split(" ")

        tags.append("dev")

        os.chdir("%s" % (self.dir))
        for t in tags:
            if t=="":
                continue
            cmd = "git clone --depth 1 --single-branch --branch %s \"file://%s\" %s" % (t,self.main_dir,t)
            print(cmd)
            os.system(cmd)

    def testVersionCompatibility(self):
        assert len(self.module_names)>1
        modules = map(__import__, self.module_names)
        assert len(modules)>1
        newest_mod = modules[len(modules)-1]

        for mod in modules:
            if mod != newest_mod:
                app = QtWidgets.QApplication(sys.argv)
                win = mod.MainWindow()
                file = tempfile.mktemp()
                mod.do_save(file)
                new_win = newest_mod.MainWindow()
                new_win.do_load(file)
                os.remove(file)
                sys.exit(app.exec_())

    def tearDown(self):
        os.chdir(self.main_dir)
        shutil.rmtree(self.dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()