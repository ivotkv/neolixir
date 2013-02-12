from unittest import TestCase
from metadata import metadata as m

class Container(object):
    pass

class BaseTest(TestCase):

    shared = Container()
    
    def setUp(self):
        m.session.clear()
    
    def tearDown(self):
        m.session.clear()
