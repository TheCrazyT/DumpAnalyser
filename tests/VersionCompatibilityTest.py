import tempfile
import importlib
import sys
import os
import shutil
from PyQt5 import QtWidgets
import unittest

class VersionCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.module_names = []
        self.dir = tempfile.mkdtemp()
        sys.path.append(self.dir)
        self.main_dir = os.getcwd()

        p = os.popen("git tag -l")
        tags_str = "%s" % p.read().replace("\n","")
        p.close()
        tags = tags_str.split(" ")

        tags.append("dev")

        os.chdir("%s" % (self.dir))
        self.module_directory = []
        for t in tags:
            if t=="":
                continue
            clean_name = "m%s" % t.replace(".","xxx")
            self.module_names.append("%s.MainWindow" % clean_name)
            self.module_directory.append("%s/%s" % (self.dir,clean_name))
            cmd = "git clone --depth 1 --single-branch --branch %s \"file://%s\" %s" % (t,self.main_dir,clean_name)
            os.system(cmd)
            print("files in %s" % clean_name)
            os.system("ls %s" % clean_name)

    def testVersionCompatibility(self):
        assert len(self.module_names)>1

        initialized_modules = []
        print(self.module_names)
        cnt = 0
        for m in self.module_names:
            print("chdir %s" % self.module_directory[cnt])
            os.chdir(self.module_directory[cnt])
            mod = importlib.import_module(m)
            cnt += 1
            newest_mod = mod
            initialized_modules.append(mod)
        print("number of modules %d;" % cnt)

        x = 0
        for mod in initialized_modules:
            if mod != newest_mod:
                print("chdir %s" % self.module_directory[x])
                os.chdir(self.module_directory[x])
                app = QtWidgets.QApplication(sys.argv)
                win = mod.MainWindow()
                file = tempfile.mktemp()
                print("do_save")
                win.do_save(file)
                os.chdir(self.module_directory[len(self.module_directory)-1])
                new_win = newest_mod.MainWindow()
                print("do_load")
                new_win.do_load(file)
                os.remove(file)
            x += 1

    def tearDown(self):
        os.chdir(self.main_dir)
        os.system("rm -f -R %s" % self.dir)

if __name__ == "__main__":
    unittest.main()