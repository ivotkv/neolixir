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

        # relview
        self.assertTrue(n1.likes is n1.relview('likes'))
        self.assertTrue(n1.liked_by is n1.relview('liked_by'))
        self.assertTrue(n1.relview('likes') is not n1.relview('liked_by'))
        self.assertTrue(n2.likes is n2.relview('likes'))
        self.assertTrue(n1.relview('likes') is not n2.relview('likes'))

        # no multiples by default
        self.assertTrue(len(n1.likes) == 0)
        self.assertTrue(len(n2.liked_by) == 0)
        n1.likes.append(n2)
        self.assertTrue(len(n1.likes) == 1)
        self.assertTrue(len(n2.liked_by) == 1)
        n1.likes.append(n2)
        n2.liked_by.append(n1)
        self.assertTrue(len(n1.likes) == 1)
        self.assertTrue(len(n2.liked_by) == 1)
        n1.likes.remove(n2)
        self.assertTrue(len(n1.likes) == 0)
        self.assertTrue(len(n2.liked_by) == 0)

        # self-reference
        n1.likes.append(n1)
        self.assertTrue(n1 in n1.likes)
        self.assertTrue(n1 in n1.liked_by)
        n1.likes.remove(n1)
        self.assertTrue(n1 not in n1.likes)
        self.assertTrue(n1 not in n1.liked_by)

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

    def test07_onerels(self):
        n1 = SubNode()
        n2 = SubNode()
        self.assertTrue(n1.one_in is None)
        self.assertTrue(n2.one_out is None)
        n1.one_in = n2
        self.assertTrue(n1.one_in is n2)
        self.assertTrue(isinstance(n1.relview('one_in').rel(), SubRel))
        self.assertTrue(n2.one_out is n1)
        self.assertTrue(isinstance(n2.relview('one_out').rel(), SubRel))
        self.assertTrue(n1.relview('one_in').rel() is n2.relview('one_out').rel())
        n1.one_in = None
        self.assertTrue(n1.one_in is None)
        self.assertTrue(n2.one_out is None)
        n1.one_in = n2
        n2.one_out = None
        self.assertTrue(n1.one_in is None)
        self.assertTrue(n2.one_out is None)
        n1.one_in = n1
        self.assertTrue(n1.one_in is n1)
        self.assertTrue(n1.one_out is n1)
        n1.one_in = None
        self.assertTrue(n1.one_in is None)
        self.assertTrue(n1.one_out is None)

        # relview
        n1.one_in = None
        self.assertTrue(n1.relview('one_in') is not n1.one_in)
        self.assertTrue(len(n1.relview('one_in')) == 0)
        n1.one_in = n2
        self.assertTrue(n1.relview('one_in') is not n1.one_in)
        self.assertTrue(len(n1.relview('one_in')) == 1)
        self.assertTrue(n1.relview('one_in')[0] is n2)

    def test08_multiplerels(self):
        n1 = SubNode()
        n2 = SubNode()
        self.assertTrue(len(n1.multiple_in) is 0)
        self.assertTrue(len(n2.multiple_out) is 0)
        n1.multiple_in.append(n2)
        self.assertTrue(len(n1.multiple_in) is 1)
        self.assertTrue(len(n2.multiple_out) is 1)
        n1.multiple_in.append(n2)
        self.assertTrue(len(n1.multiple_in) is 2)
        self.assertTrue(len(n2.multiple_out) is 2)
        self.assertTrue(len(set(n1.multiple_in)) is 1)
        self.assertTrue(len(set(n2.multiple_out)) is 1)
        self.assertTrue(list(set(n1.multiple_in))[0] is n2)
        self.assertTrue(list(set(n2.multiple_out))[0] is n1)
        n1.multiple_in.remove(n1.multiple_in.rel(n2)[0])
        self.assertTrue(len(n1.multiple_in) is 1)
        self.assertTrue(len(n2.multiple_out) is 1)
        n1.multiple_in.append(n2)
        n2.multiple_out.append(n1)
        self.assertTrue(len(n1.multiple_in) is 3)
        self.assertTrue(len(n2.multiple_out) is 3)
        self.assertTrue(n2 in n1.multiple_in)
        self.assertTrue(n2 not in n1.multiple_out)
        self.assertTrue(n1 in n2.multiple_out)
        self.assertTrue(n1 not in n2.multiple_in)

    def test09_expunge(self):
        n1 = SubNode()
        n2 = SubNode()
        rel = n1.likes.append(n2)
        self.assertTrue(n1 in m.session.phantomnodes)
        self.assertTrue(n2 in m.session.phantomnodes)
        self.assertTrue(rel in m.session.relmap)
        n1.expunge()
        self.assertTrue(n1 not in m.session.phantomnodes)
        self.assertTrue(n2 in m.session.phantomnodes)
        self.assertTrue(rel not in m.session.relmap)
