from random import randint
from basetest import BaseTest
from models import *

class TestNodeQuery(BaseTest):

    def test01_query_identity(self):
        self.shared.test_id = randint(0, 2**30)
        n = SubNode(test_id=self.shared.test_id)
        n.save()
        self.assertTrue(SubNode.query(test_id=self.shared.test_id)[0] is n)
    
    def test02_query_polymorphic(self):
        n = Node.query(test_id=self.shared.test_id)[0]
        self.assertTrue(isinstance(n, SubNode))
        self.assertTrue(len(SubSubNode.query(test_id=self.shared.test_id)) == 0)
        n.delete()
        n.save()
