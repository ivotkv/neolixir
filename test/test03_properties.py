from basetest import BaseTest
from models import *

class TestProperties(BaseTest):

    def test01_save(self):
        n = SubNode()
        n.properties['test_property'] = 'test_value'
        n.save()
        n.expunge()
        n2 = SubNode(n.id)
        self.assertTrue(n2.properties['test_property'] == 'test_value')
        n2.delete()
        n2.save()
