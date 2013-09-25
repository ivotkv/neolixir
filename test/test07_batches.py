from basetest import BaseTest
from models import *

class TestBatches(BaseTest):

    def test01_index(self):
        batch = m.batch()
        index = NodeIndex('BatchTestIndex')
        index.clear()

        # test creating and uniqueness
        batch.index(index, 'node', '1', SubNode())
        batch.submit()
        n1 = index.get('node', '1')[0]
        self.assertTrue(len(m.session.phantomnodes) == 0)
        self.assertTrue(len(m.session.nodes) == 1)
        self.assertTrue(isinstance(n1, SubNode))

        batch.index(index, 'node', '1', SubNode())
        batch.submit()
        self.assertTrue(len(index.get('node', '1')) == 1)
        self.assertTrue(index.get('node', '1')[0] is n1)
        self.assertTrue(len(m.session.phantomnodes) == 0)
        self.assertTrue(len(m.session.nodes) == 1)

        # test indexing an existing node
        batch.index(index, 'node', '2', n1)
        batch.submit()
        self.assertTrue(n1 in m.session.nodes.values())
        self.assertTrue(len(index.get('node', '2')) == 1)
        self.assertTrue(index.get('node', '2')[0] is n1)

        batch.index(index, 'node', '2', n1)
        batch.index(index, 'node', '2', SubNode())
        batch.submit()
        self.assertTrue(len(m.session.phantomnodes) == 0)
        self.assertTrue(len(m.session.nodes) == 1)
        self.assertTrue(n1 in m.session.nodes.values())
        self.assertTrue(len(index.get('node', '2')) == 1)
        self.assertTrue(index.get('node', '2')[0] is n1)

        # test return values
        def callback(self, n1, response):
            self.assertTrue(response is n1)
        batch.index(index, 'node', '3', n1)
        batch.request_callback(callback, self, n1)
        batch.index(index, 'node', '3', SubNode())
        batch.request_callback(callback, self, n1)
        batch.submit()

        def callback(self, m, cls, response):
            self.assertTrue(isinstance(response, cls))
            self.assertTrue(index.get('node', '4')[0] is response)
            self.assertTrue(len(m.session.phantomnodes) == 0)
        batch.index(index, 'node', '4', SubNode())
        batch.request_callback(callback, self, m, SubNode)
        batch.submit()

        n2 = SubNode()
        def callback(self, m, n2, response):
            self.assertTrue(response is n2)
            self.assertTrue(len(m.session.phantomnodes) == 0)
        batch.index(index, 'node', '5', n2)
        batch.request_callback(callback, self, m, n2)
        batch.submit()

        # test that __instance_of__ relationship was created
        self.assertTrue(n1 in SubNode.query.all())
