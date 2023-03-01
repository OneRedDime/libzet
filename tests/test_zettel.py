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
        keys = sorted(z.attributes)
        self.assertEqual(keys, list(z.attributes.keys()))

    def test_humanized_date(self):
        """ Values that contain "date" should be parsed.
        """
        z = Zettel.createFromRst(f'{resources}/human-date.rst')
        exp_date = parse_date('today')
        exp_duedate = parse_date('next wednesday')

        self.assertEqual(exp_date, z.creation_date)
        self.assertEqual(exp_duedate, z.due_date)

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
        zettel = Zettel.createFromRst(path)

        self.assertEqual('today', zettel.title)
        self.assertEqual('Today is today\n', zettel.headings['notes'])
        self.assertEqual('heading body\n', zettel.headings['today heading'])
        self.assertEqual('heading body\n\nmultiline\n', zettel.headings['second heading'])
        self.assertEqual('today-id', zettel.attributes['id'])
        self.assertEqual(['birthday'], zettel.attributes['tags'])

    def test_basic_md_parsing(self):
        """ Single md zettel.
        """
        path = f'{resources}/md/today.md'
        zettel = Zettel.createFromMd(path)

        self.assertEqual('today', zettel.title)
        self.assertEqual('Today is today\n', zettel.headings['notes'])
        self.assertEqual('heading body\n', zettel.headings['today heading'])
        self.assertEqual('heading body\n\nmultiline\n', zettel.headings['second heading'])
        self.assertEqual('today-id', zettel.attributes['id'])
        self.assertEqual(['birthday'], zettel.attributes['tags'])

    def test_md_creation_and_str_back(self):
        """ MD text should be re-created as it was read.
        """
        path = f'{resources}/md/today.md'
        zettel = Zettel.createFromMd(path)

        with open(path) as f:
            exp = f.read()

        self.assertEqual(exp, zettel.getMd())

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

        self.assertEqual(all_, [today, tomorrow])

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

        self.assertEqual(all_, [today, tomorrow])
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
        f = filtered_zettels(zettels, '"birthday" in f.tags', letter='f')

        self.assertEqual(f[0], zettels[0])
        self.assertEqual(1, len(f))

        # Just search for the other one
        f = filtered_zettels(zettels, 'z.id == "tomorrow-id"')

        self.assertEqual(f[0], zettels[1])
        self.assertEqual(1, len(f))

    def test_filtered_zettels_no_member(self):
        """ Test basic filtering zettels
        """
        path = f'{resources}/md'
        all_path = f'{path}/all.md'

        zettels = get_zettels_from_md(all_path)

        f = filtered_zettels(zettels, '"not_exist" in f', letter='f')
        self.assertEqual([], f)


if __name__ == '__main__':
    unittest.main()
