from basetest import BaseTest
from models import *

class TestRelationships(BaseTest):

    def test01_mapper(self):
        n1 = SubNode()
        n2 = SubNode()
        r = Relationship((n1, 'test', n2))
        self.assertTrue(r in n1.relationships)
        self.assertTrue(r in n2.relationships)
        r.delete()
        self.assertTrue(r not in n1.relationships)
        self.assertTrue(r not in n2.relationships)

    def test02_descriptors(self):
        n1 = SubNode()
        n2 = SubNode()
        self.assertTrue(len(n1.likes) == 0)
        self.assertTrue(len(n1.liked_by) == 0)
        r = Relationship((n1, 'like', n2))
        self.assertTrue(r in n1.likes)
        self.assertTrue(n2 in n1.likes.nodes())
        self.assertTrue(r in n2.liked_by)
        self.assertTrue(n1 in n2.liked_by.nodes())
        r.delete()
        n1.liked_by.append(n2)
        self.assertTrue(n2 in n1.liked_by.nodes())
        self.assertTrue(n1 in n2.likes.nodes())
        n2.likes.remove(n1)
        self.assertTrue(n2 not in n1.liked_by.nodes())
        self.assertTrue(n1 not in n2.likes.nodes())

    def test03_save(self):
        n1 = SubNode()
        n2 = SubNode()
        r = SubRel((n1, 'test', n2))
        m.session.commit()
        self.assertTrue(r.id is not None)
        self.shared.id = r.id

    def test04_load(self):
        r = Relationship(self.shared.id)
        self.assertTrue(r.id == self.shared.id)
        self.assertTrue(isinstance(r, SubRel))
        self.assertTrue(r.type == 'test')
        self.assertTrue(isinstance(r.start, SubNode))
        self.assertTrue(isinstance(r.end, SubNode))

    def test05_delete(self):
        r = Relationship(self.shared.id)
        n1 = r.start
        n2 = r.end
        n1.delete()
        self.assertTrue(r.is_deleted())
        self.assertTrue(not n2.is_deleted())
        n2.delete()
        m.session.commit()
        self.assertRaises(ResourceNotFound, Relationship, self.shared.id)
