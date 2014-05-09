from basetest import BaseTest
from models import *

class TestIndexes(BaseTest):

    def test01_node_basics(self):
        i = NodeIndex('TestNodeIndex')
        i.clear()
        res = i.get('key', 'value')
        self.assertTrue(isinstance(res, list))
        self.assertTrue(len(res) == 0)
        res = i.get('key', 'value', SubNode())
        self.assertTrue(isinstance(res, SubNode))
        res = i.get('key', 'value')
        self.assertTrue(len(res) == 1 and isinstance(res[0], SubNode))
        i.clear()
        res = i.get('key', 'value')
        self.assertTrue(len(res) == 0)
