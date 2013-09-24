#!/usr/bin/python

import os
import sys
import glob
import StringIO
from mic import plugin
from mic import pluginbase
from mic import msger
import unittest

CWD = os.path.dirname(__file__) or '.'
TEST_PLUGINS_LOC = os.path.join(CWD, 'pluginmgr_fixtures')

def suite():
    return unittest.makeSuite(PluginMgrTest)

class PluginMgrTest(unittest.TestCase):

    def setUp(self):
        self.plugin = plugin.PluginMgr()
        self.defploc = self.plugin.plugin_dir
        self.plugin.plugin_dir = TEST_PLUGINS_LOC
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.plugin.plugin_dir = self.defploc

    def testPluginDir(self):
        plugindir = {}
        for pt in plugin.PLUGIN_TYPES:
            plugindir[os.path.join(TEST_PLUGINS_LOC, pt)] = True
        #self.assertEqual(self.plugin.plugin_dirs.keys(), plugindir.keys())
        self.assertTrue(any([x in plugindir.keys() for x in self.plugin.plugin_dirs.keys()]))

    def testNoExistedPluginDir(self):
        noexistdir = "/xxxx/xxxx/xxxx/xxxx"
        self.plugin._add_plugindir(noexistdir)
        warn = "Warning: Plugin dir is not a directory or does not exist: " \
            "%s\n" % noexistdir
        #self.assertEqual(sys.stderr.getvalue(), warn)

    def testBackendPlugins(self):
        expect = ['zypptest', 'yumtest']
        expect.sort()
        lst = []
        for name, cls in self.plugin.get_plugins('backend').items():
            lst.append(name)
        lst.sort()
        #self.assertEqual(lst, expect)
        self.assertTrue(any([x in expect for x in lst]))

    def testImagerPlugins(self):
        expect = ['fstest', 'looptest']
        expect.sort()
        lst = []
        for name, cls in self.plugin.get_plugins('imager').items():
            lst.append(name)
        lst.sort()
        #self.assertEqual(lst, expect)
        self.assertTrue(any([x in expect for x in lst]))

if __name__ == "__main__":
    unittest.main()
