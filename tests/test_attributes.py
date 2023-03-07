import os
import unittest

from libzet.Attributes import Attributes
from libzet.NoCompare import NoCompare


class TestAttributes(unittest.TestCase):

    def test_basic_creation(self):
        """ Attributes can be loaded from yaml.
        """
        s = '''---
        greeting: hello
        farewell: goodbye
        '''

        a = Attributes.fromYaml(s)
        self.assertEqual('hello', a['greeting'])
        self.assertEqual('goodbye', a['farewell'])

    def test_nocompare(self):
        """ Non-existent keys should return NoCompare
        """
        a = Attributes()
        x = a['test']
        self.assertTrue(type(x) is NoCompare)

    def test_nocompare_conditional(self):
        """ Non-existent keys should always return false on compare.
        """
        a = Attributes()
        x = 0

        self.assertFalse(a['x'] == x)
        self.assertFalse(a['x'] != x)
        self.assertFalse(a['x'] < x)
        self.assertFalse(a['x'] > x)
        self.assertFalse(a['x'] >= x)
        self.assertFalse(a['x'] <= x)


if __name__ == '__main__':
    unittest.main()
