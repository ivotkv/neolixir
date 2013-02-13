from random import randint
from basetest import BaseTest
from models import *

class TestNodeQuery(BaseTest):

    def test01_query_identity(self):
        self.shared.test_id = randint(0, 2**30)
        n = SubNode(test_id=self.shared.test_id)
        n.save()
        self.assertTrue(SubNode.get_by(test_id=self.shared.test_id) is n)
    
    def test02_query_polymorphic(self):
        n = Node.get_by(test_id=self.shared.test_id)
        self.assertTrue(isinstance(n, SubNode))
        self.assertRaises(NoResultFound, SubSubNode.get_by, test_id=self.shared.test_id)
        n.delete()
        n.save()
