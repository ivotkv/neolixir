from basetest import BaseTest
from models import *

class TestNodes(BaseTest):

    def test01_create(self):
        n = SubNode()
        self.assertTrue(n.id is None)
        n.save()
        self.assertTrue(n.id is not None)
        self.shared.id = n.id

    def test02_load(self):
        n = Node(self.shared.id)
        self.assertEqual(n.id, self.shared.id)
        self.assertTrue(isinstance(n, SubNode))
        n2 = Node(self.shared.id)
        self.assertTrue(n2 is n)

    def test03_expunge(self):
        n = Node(self.shared.id)
        n.expunge()
        n2 = Node(self.shared.id)
        self.assertTrue(n2 is not n)

    def test04_delete(self):
        n = Node(self.shared.id)
        n.delete()
        self.assertTrue(n.is_deleted())
        n.save()
        self.assertTrue(Node(self.shared.id) is None)
