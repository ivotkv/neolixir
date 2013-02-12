from basetest import BaseTest
from models import *

class TestMetadata(BaseTest):

    def setUp(self):
        super(TestMetadata, self).setUp()
        self.q = "start "
        self.q += "n=node({0}), ".format(m.classnode(Node).id)
        self.q += "s=node({0}), ".format(m.classnode(SubNode).id)
        self.q += "ss=node({0}) ".format(m.classnode(SubSubNode).id)

    def test01_consistency(self):
        self.assertTrue(m.classnode(Node) is m.classnode(Node))
        self.assertTrue(m.classnode(Node) is not m.classnode(SubNode))
        self.assertTrue(m.class_from_classnode(m.classnode(Node)) is Node)

    def test02_init(self):
        m.init()
        q = self.q + "match p=ss-[:EXTENDS]->s-[:EXTENDS]->n return p"
        self.assertEqual(len(m.cypher(q)), 1)

    def test03_initreset(self):
        q = self.q + "create ss-[r:EXTENDS]->n return r"
        self.assertEqual(len(m.cypher(q)), 1)
        m.init(reset=True)
        q = self.q + "match ss-[r:EXTENDS]->n return r"
        self.assertEqual(len(m.cypher(q)), 0)
