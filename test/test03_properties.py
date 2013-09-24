from basetest import BaseTest
from models import *

class TestProperties(BaseTest):

    def test01_node_properties(self):
        n = SubNode()
        n.properties['test_property1'] = 'test_value1'
        m.session.commit()
        n.properties['test_property2'] = 'test_value2'
        m.session.commit()
        n.expunge()
        n = SubNode(n.id)
        self.assertTrue(n.properties['test_property1'] == 'test_value1')
        self.assertTrue(n.properties['test_property2'] == 'test_value2')

    def test01_rel_properties(self):
        n1 = SubNode()
        n2 = SubNode()
        rel = n1.likes.append(n2)
        rel.properties['test_property1'] = 'test_value1'
        m.session.commit()
        rel.properties['test_property2'] = 'test_value2'
        m.session.commit()
        rel.expunge()
        rel = Relationship(rel.id)
        self.assertTrue(rel.properties['test_property1'] == 'test_value1')
        self.assertTrue(rel.properties['test_property2'] == 'test_value2')
