from basetest import BaseTest
from models import *

class TestProperties(BaseTest):

    def test03_interface_fields(self):
        self.assertTrue(hasattr(SubSubNode, 'interface_field'))
        self.assertTrue('interface_field' in SubSubNode._descriptors)
        self.assertTrue(SubSubNode.interface_field.name == 'interface_field')
        n = SubSubNode()
        self.assertTrue(hasattr(n, 'interface_field'))
        self.assertTrue('interface_field' in n._descriptors)
        self.assertTrue(n.interface_field == 'interface_field_value')
        n.interface_field = 'new_value'
        self.assertTrue(n.interface_field == 'new_value')
        self.assertTrue(n.properties['interface_field'] == 'new_value')

    def test04_enums(self):
        n = SubSubNode()
        self.assertTrue(n.enum == 'default')
        n.enum = 'value1'
        self.assertTrue(n.enum == 'value1')
        n.enum = 'value2'
        self.assertTrue(n.enum == 'value2')
        try:
            n.enum = 'invalid'
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
        self.assertTrue(n.enum == 'value2')
        n.enum = 'default'
        self.assertTrue(n.enum == 'default')
