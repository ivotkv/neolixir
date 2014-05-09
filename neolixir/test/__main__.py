import os
import sys
from glob import glob
from unittest import TestSuite, defaultTestLoader as loader, TextTestRunner

pkgdir = os.path.dirname(os.path.dirname(__file__))
os.chdir(pkgdir)

sys.path.pop(0)
sys.path.insert(0, pkgdir)

modules = [x.split('/')[-1].split('.py')[0] for x in glob(pkgdir + '/test/test*.py')]

suite = TestSuite((loader.loadTestsFromName('test.' + x) for x in sorted(modules)))
TextTestRunner(verbosity=2).run(suite)
