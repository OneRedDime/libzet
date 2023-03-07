import os
import unittest

from superdate import parse_date

from libzet.Zettel import Zettel, get_zettels_from_md, get_zettels_from_rst, filtered_zettels


resources = '{}/resources'.format(os.path.dirname(__file__))


class TestZettel(unittest.TestCase):

    def test_rst_creation_and_str_back(self):
        """ Zettels can be created from RST text.
        """
        with open(f'{resources}/basic.rst') as f:
            exp = f.read()

        z = Zettel.createFromRst(exp)

        self.assertEqual(exp, z.getRst())

    def test_alphabetized_attributes(self):
        """ Zettels should alphabetize attributes when printing.
        """
        z = Zettel.createFromRst(f'{resources}/out-of-order.rst')
        z = Zettel.createFromRst(z.getRst())
        keys = sorted(z.attrs)
        self.assertEqual(keys, list(z.attrs.keys()))

    def test_humanized_date(self):
        """ Values that contain "date" should be parsed.
        """
        z = Zettel.createFromRst(f'{resources}/human-date.rst')
        exp_date = parse_date('today')
        exp_duedate = parse_date('next wednesday')

        self.assertEqual(exp_date, z.attrs['creation_date'])
        self.assertEqual(exp_duedate, z.attrs['due_date'])

    def test_trailing_space(self):
        """ Zettel parsing should trim trailing spaces.
        """
        z = Zettel.createFromRst(f'{resources}/trailing-lines.rst')
        with open(f'{resources}/basic.rst') as f:
            exp = f.read().strip() + '\n'

        self.assertEqual(exp, z.getRst())

    def test_basic_rst_parsing(self):
        """ Single rst zettel.
        """
        path = f'{resources}/rst/today.rst'
        z = Zettel.createFromRst(path)

        self.assertEqual('today', z.title)
        self.assertEqual('Today is today\n', z.headings['_notes'])
        self.assertEqual('heading body\n', z.headings['today heading'])
        self.assertEqual('heading body\n\nmultiline\n', z.headings['second heading'])
        self.assertEqual('today-id', z.attrs['id'])
        self.assertEqual(['birthday'], z.attrs['tags'])

    def test_basic_md_parsing(self):
        """ Single md zettel.
        """
        path = f'{resources}/md/today.md'
        z = Zettel.createFromMd(path)

        self.assertEqual('today', z.title)
        self.assertEqual('Today is today\n', z.headings['_notes'])
        self.assertEqual('heading body\n', z.headings['today heading'])
        self.assertEqual('heading body\n\nmultiline\n', z.headings['second heading'])
        self.assertEqual('today-id', z.attrs['id'])
        self.assertEqual(['birthday'], z.attrs['tags'])

    def test_md_creation_and_str_back(self):
        """ MD text should be re-created as it was read.
        """
        path = f'{resources}/md/today.md'
        z = Zettel.createFromMd(path)

        with open(path) as f:
            exp = f.read()

        self.assertEqual(exp, z.getMd())

    def test_compound_rst_parsing(self):
        """ Multiple zettels in one file.
        """
        path = f'{resources}/rst'

        today_path = f'{path}/today.rst'
        tomorrow_path = f'{path}/tomorrow.rst'
        all_path = f'{path}/all.rst'

        today = Zettel.createFromRst(today_path)
        tomorrow = Zettel.createFromRst(tomorrow_path)
        all_ = get_zettels_from_rst(all_path)

        self.assertEqual([x.title for x in all_], [today.title, tomorrow.title])

    def test_compound_md_parsing(self):
        """ Multiple zettels in one file.
        """
        path = f'{resources}/md'

        today_path = f'{path}/today.md'
        tomorrow_path = f'{path}/tomorrow.md'
        all_path = f'{path}/all.md'

        today = Zettel.createFromMd(today_path)
        tomorrow = Zettel.createFromMd(tomorrow_path)
        all_ = get_zettels_from_md(all_path)

        self.assertEqual([x.title for x in all_], [today.title, tomorrow.title])
        self.assertEqual(all_[0].headings, today.headings)
        self.assertEqual(all_[1].headings, tomorrow.headings)

    def test_filtered_zettels(self):
        """ Test basic filtering zettels
        """
        path = f'{resources}/md'
        all_path = f'{path}/all.md'

        zettels = get_zettels_from_md(all_path)

        # get whole list
        f = filtered_zettels(zettels)

        self.assertEqual(f[0], zettels[0])
        self.assertEqual(f[1], zettels[1])
        self.assertEqual(2, len(f))

        # search in tags
        # TODO: checking 'x in z.tags' will fail if tags is loaded as None
        f = filtered_zettels(zettels, '"birthday" in f.attrs["tags"]', letter='f')

        self.assertEqual(f[0].title, zettels[0].title)
        self.assertEqual(1, len(f))

        # Just search for the other one
        f = filtered_zettels(zettels, 'z.attrs["id"] == "tomorrow-id"')

        self.assertEqual(f[0].title, zettels[1].title)
        self.assertEqual(1, len(f))

    def test_filtered_zettels_no_member(self):
        """ Test basic filtering zettels
        """
        path = f'{resources}/md'
        all_path = f'{path}/all.md'

        zettels = get_zettels_from_md(all_path)

        f = filtered_zettels(zettels, '"not_exist" in f.attrs', letter='f')
        self.assertEqual([], f)


if __name__ == '__main__':
    unittest.main()
