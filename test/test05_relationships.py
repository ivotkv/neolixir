from basetest import BaseTest
from models import *

class TestRelationships(BaseTest):

    def test01_mapper(self):
        relmap = m.session.relmap
        n1 = SubNode()
        n2 = SubNode()
        r = Relationship((n1, 'test', n2))
        self.assertTrue(r.start is n1)
        self.assertTrue(r.type is 'test')
        self.assertTrue(r.end is n2)
        self.assertTrue(r in relmap.start[(n1, 'test')])
        self.assertTrue(r in relmap.end[(n2, 'test')])
        r.delete()
        self.assertTrue(r not in relmap.start[(n1, 'test')])
        self.assertTrue(r not in relmap.end[(n2, 'test')])

    def test02_descriptors(self):
        n1 = SubNode()
        n2 = SubNode()
        self.assertTrue(len(n1.likes) == 0)
        self.assertTrue(len(n1.liked_by) == 0)
        r = Relationship((n1, 'like', n2))
        self.assertTrue(r in n1.likes)
        self.assertTrue(n2 in n1.likes)
        self.assertTrue(r in n2.liked_by)
        self.assertTrue(n1 in n2.liked_by)
        r.delete()
        n1.liked_by.append(n2)
        self.assertTrue(n2 in n1.liked_by)
        self.assertTrue(n1 in n2.likes)
        n2.likes.remove(n1)
        self.assertTrue(n2 not in n1.liked_by)
        self.assertTrue(n1 not in n2.likes)

    def test03_index_map(self):
        n1 = SubNode()
        n2 = SubNode()
        n1.likes.append(n2)
        self.assertTrue(n1.likes[0] is n2)
        self.assertTrue(isinstance(n1.likes.rel(n1.likes[0]), SubRel))
        self.assertTrue(n1.likes.node(n1.likes.rel(n1.likes[0])) is n2)

    def test04_save(self):
        n1 = SubNode()
        n2 = SubNode()
        r = SubRel((n1, 'test', n2))
        m.session.commit()
        self.assertTrue(r.id is not None)
        self.shared.id = r.id

    def test05_load(self):
        r = Relationship(self.shared.id)
        self.assertTrue(r.id == self.shared.id)
        self.assertTrue(isinstance(r, SubRel))
        self.assertTrue(r.type == 'test')
        self.assertTrue(isinstance(r.start, SubNode))
        self.assertTrue(isinstance(r.end, SubNode))

    def test06_delete(self):
        r = Relationship(self.shared.id)
        n1 = r.start
        n2 = r.end
        n1.delete()
        self.assertTrue(r.is_deleted())
        self.assertTrue(not n2.is_deleted())
        n2.delete()
        m.session.commit()
        self.assertRaises(ResourceNotFound, Relationship, self.shared.id)
