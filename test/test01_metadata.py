from basetest import BaseTest
from models import *

class TestMetadata(BaseTest):

    def setUp(self):
        super(TestMetadata, self).setUp()
        self.q = "start "
        self.q += "n=node({0}), ".format(Node.classnode.id)
        self.q += "s=node({0}), ".format(SubNode.classnode.id)
        self.q += "ss=node({0}) ".format(SubSubNode.classnode.id)

    def test01_init(self):
        m.init()
        q = self.q + "match p=ss-[:EXTENDS]->s-[:EXTENDS]->n return p"
        self.assertEqual(len(m.cypher(q)), 1)

    def test02_initreset(self):
        q = self.q + "create ss-[r:EXTENDS]->n return r"
        self.assertEqual(len(m.cypher(q)), 1)
        m.init(reset=True)
        q = self.q + "match ss-[r:EXTENDS]->n return r"
        self.assertEqual(len(m.cypher(q)), 0)