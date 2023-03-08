import os
import unittest

from superdate import parse_date

from libzet import Zettel
from libzet.parsing import str_to_zettels, zettels_to_str


resources = '{}/resources'.format(os.path.dirname(__file__))


class TestParsing(unittest.TestCase):

    def test_compound_rst_parsing(self):
        """ Multiple zettels in one rst file.
        """
        with open(f'{resources}/rst/basic.rst') as f:
            z = Zettel.createFromRst(f.read())

        s = zettels_to_str([z, z], 'rst')
        act = str_to_zettels(s, 'rst')

        self.assertEqual(2, len(act))
        self.assertFalse(all([z is x for x in act]))
        self.assertFalse(act[0] is act[1])

        self.assertEqual(z.title, act[0].title)
        self.assertEqual(z.headings, act[0].headings)
        self.assertEqual(z.attrs, act[0].attrs)

        self.assertEqual(act[0].title, act[1].title)
        self.assertEqual(act[0].headings, act[1].headings)
        self.assertEqual(act[0].attrs, act[1].attrs)

    def test_compound_md_parsing(self):
        """ Multiple zettels in one md file.
        """
        with open(f'{resources}/md/basic.md') as f:
            z = Zettel.createFromMd(f.read())

        s = zettels_to_str([z, z], 'md')
        act = str_to_zettels(s, 'md')

        self.assertEqual(2, len(act))
        self.assertFalse(all([z is x for x in act]))
        self.assertFalse(act[0] is act[1])

        self.assertEqual(z.title, act[0].title)
        self.assertEqual(z.headings, act[0].headings)
        self.assertEqual(z.attrs, act[0].attrs)

        self.assertEqual(act[0].title, act[1].title)
        self.assertEqual(act[0].headings, act[1].headings)
        self.assertEqual(act[0].attrs, act[1].attrs)


if __name__ == '__main__':
    unittest.main()
