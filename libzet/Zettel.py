import os
import re
import yaml

from icalendar import Event

from libzet.Attributes import Attributes
from libzet.parse_duration import parse_duration


rst_sep = '.. end-zettel'
md_sep = '<!--- end-zettel --->'


class SkipZettel(Exception):
    """ Custom functions should raise this to skip processing a Zettel.
    """
    pass


def readdir_(d):
    """ Same as OS. walk executed at the first level.

    Returns:
        A 3-tuple. First entry is the root (d), second is a list of all
        directory entries within d, and the third is a list of names of
        regular files.
    """
    d = d.rstrip(os.path.sep)
    if not os.path.isdir(d):
        raise ValueError('"{}" is not a directory.'.format(d))

    for root, dirs, files in os.walk(d):
        return root, dirs, files


# Find heading points.
def _is_rst_heading(s):
    s = s.strip()
    return s.startswith('=') and s.endswith('=')


def _is_md_heading(s):
    s = s.strip()
    return s.startswith('# ') or s.startswith('## ')


def get_zettels_from_md(md):
    """ Parse many zettels out of markdown text.

    Zettels are separated by md_sep

    Args:
        md: MD text or file to parse.

    Returns:
        List of zettels parsed from the string.
    """
    if os.path.exists(md):
        with open(md) as f:
            md = f.read()

    md = md.strip()
    if not md:
        return []

    # Markdown zettels are terminated by a line containing only this string.
    texts = md.split(md_sep)
    if not texts[-1]:
        texts.pop()

    zettels = []

    for t in texts:
        zettels.append(Zettel.createFromMd(t))

    return zettels


def get_zettels_from_rst(rst):
    if os.path.exists(rst):
        with open(rst) as f:
            rst = f.read()

    rst = rst.strip()
    if not rst:
        return []

    texts = rst.split(rst_sep)
    if not texts[-1]:
        texts.pop()

    zettels = []
    for t in texts:
        zettels.append(Zettel.createFromRst(t))

    return zettels


def str_to_zettels(text, zettel_format):
    """ Convert a str to a list of zettels.

    The return from this function can be passed to zettels_to_str.

    Args:
        text: Text to convert to zettels.
        zettel_format: 'rst' or 'md'.

    Returns:
        A list of Zettel references.
    """
    zettels = []
    if zettel_format == 'rst':
        zettels = get_zettels_from_rst(text)
    elif zettel_format == 'md':
        zettels = get_zettels_from_md(text)

    return zettels


def zettels_to_str(zettels, zettel_format, headings=None):
    """ Return many zettels as a str.

    The output from this function can be passed to str_to_zettels.

    Args:
        zettels: List of zettels to print.
        zettel_format: 'rst' or 'md'.

    Returns:
        A str representing the zettels
    """
    text = ''
    formats = ['rst', 'md']

    if zettel_format not in formats:
        raise ValueError(f'zettel_format must be in {formats}')

    if zettel_format == 'rst':
        text = [x.getRst(headings) for x in zettels]
        text = f'\n{rst_sep}\n\n\n'.join(sorted([x for x in text if x]))
    elif zettel_format == 'md':
        text = [x.getMd(headings) for x in zettels]
        text = f'\n{md_sep}\n\n\n'.join(sorted([x for x in text if x]))

    return text


def load_zettel(path, zettel_format, fun=lambda z: None):
    """ Load a single Zettel from the filesystem.

    The zettel will gain a new _loadpath attribute. Useful to
    know where to write it back.

    Args:
        path: Path to zettel.
        zettel_format: rst or md.
        fun: Call this function on the zettel as it's loaded from disk.
            Raise SkipZettel from fun to avoid loading a zettel.

    Returns:
        A reference to the newly loaded zettel.
    """
    with open(path) as f:
        z = str_to_zettels(f.read(), zettel_format)[0]

    # Guarantee _loadpath
    z.attrs['_loadpath'] = path
    fun(z)
    z.attrs['_loadpath'] = path
    return z


def load_zettels(paths, zettel_format, recurse=False, fun=lambda z: None):
    """ Load Zettels from the filesystem.

    Zettels will be updated with a _loadpath value in their attrs.
    This value is useful while zettels are being manipulated in a
    program because it is guaranteed to be unique (at least within
    that program).

    If this list is sent to save_zettels then the _loadpath will
    not be written.

    Args:
        paths: List of directories and exact paths to zettels.
        zettel_format: md or rst
        recurse: True to recurse into subdirs, False otherwise.
        fun: Call this function on each zettel as it's loaded from disk.
            If the zettel should be skipped then have this function
            raise SkipZettel.

    Returns:
        A list of zettels.

        This list may be passed to save_zettels to write
        them to the filesystem.
    """
    zettels = []

    if type(paths) is not list:
        paths = [paths]

    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f'{path} does not exist.')

        if os.path.isdir(path):
            root, dir_, files = readdir_(path)

            files = [f'{root}/{f}' for f in files if f.endswith(f'.{zettel_format}')]

            for f in files:
                try:
                    zettels.append(load_zettel(f, zettel_format, fun))
                except SkipZettel:
                    pass

            if recurse:
                for d in dir_:
                    zettels.extend(load_zettels(f'{root}/{d}', zettel_format, recurse, fun))

        elif os.path.isfile(path):
            try:
                zettels.append(load_zettel(path, zettel_format, fun))
            except SkipZettel:
                pass

        else:
            raise ValueError(f'{path} is not a regular file or directory.')

    return zettels


def save_zettels(zettels, zettel_format, fun=lambda z: None):
    """ Save zettels back to disk.

    The zettels are expected to have a _loadpath key in their attrs.
    Probably best to send the output from load_zettels to this function.

    Args:
        zettels: List of zettels.
        zettel_format: md or rst.
        fun: A callable that accepts a zettel reference. This will be called
            on each zettel before it's written back to disk.

            Raise SkipZettel from fun to avoid saving a zettel.
    """
    for z in zettels:
        loadpath = z.attrs['_loadpath']
        fun(z)
        del(z.attrs['_loadpath'])
        with open(loadpath, 'w') as f:
            f.write(zettels_to_str([z], zettel_format))


def parse_rrule(rrule):
    """ Parse an icalendar rrule str into a dict.

    Follow the ICS convention for rrules.

    https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html

    But omit the leading "RRULE:".

    Use the return of this function like this.

        event['rrule'] = parse_rrule(some_rrule))

    Arg:
        rrule: The str rrule to parse.

    Returns:
        An rrule object that can be directly set as an icalendar.Event's
        'rrule' index.

    Raises:
        ValueError if the rrule str wasn't valid.
    """
    rrule = 'RRULE:' + rrule
    s = '\n'.join(['BEGIN:VEVENT', rrule, 'END:VEVENT'])
    event = Event.from_ical(s)

    if not len(event['rrule']):
        raise ValueError('Invalid rrule')

    return event['rrule']


def filtered_zettels(zettels, filter='', letter='z'):
    """ Return a filtered list of zettels.

    Args:
        zettels: A list of zettels to filter on.
        filter: String to filter on. z is the zettel reference for each z
            in zettels. This filter must follow python3 conditional syntax.
        letter: What letter should be used to point to a zettel in the under-
            the-hood python3 list comprehension. Default is 'z'.

            eg. [z for z in zettels if eval(filter)]

    Returns:
        A filtered list of zettel references which matched the filter.
    """
    filter = filter or 'True'

    s = f'[{letter} for {letter} in zettels if {filter}]'
    return eval(s)


class Zettel:
    """ Represents a zettel.
    """
    def __init__(self, title, headings=None, attrs=None, **kwargs):
        """ Init a new Zettel.

        Args:
            title: Title of the zettel.
            headings: Dictionary of subheadings. Each heading is paired with
                a string for its zettel.

            attrs: Metadata about the zettel.

                Attributes may also be provided to the constructor via
                keyword arguments. Tasks may have additional attrs.

        Raises:
            ValueError if some attribute keys were invalid.
        """
        headings = headings or dict()
        attrs = attrs or dict()

        self.title = title
        self.headings = {k: v for k, v in headings.items()}

        # Process attrs
        self.attrs = Attributes()
        self.attrs.update(attrs)
        self.attrs.update(kwargs)

    def asIcsEvent(self, uid):
        """ Return an icalendar.Event class from this Zettel's data.

        A zettel must have either a event_begin or a due_date to be
        considered capable of turning into an ICS Event.

        This function does not support all ICS Event values. The
        supported values are...
        - uid
        - dtstamp: Initialized to the time this method was called.
        - summary
        - description
        - dtstart: as event_begin or due_date with respective *_time's
        - dtend: as event_end + end_time (optional)
        - rrule: as recurring

        Returns:
            An icalendar.Event created from this instance's data. If
            this zettel doesn't have a due_date or event_begin field then
            None will be returned.
        """
        exp = ['event_begin', 'due_date']
        if not any([x in self.attrs and self.attrs[x] for x in exp]):
            return None

        desc = self.headings['_notes'] if '_notes' in self.headings else ''

        event = Event()
        event.add('uid', uid)
        event.add('summary', self.title)
        event.add('description', desc)

        event.add('dtstamp', parse_date('today'))

        if 'event_begin' in self and self.event_begin:
            event.add('dtstart', self.event_begin.date)
        elif 'due_date' in self and self.due_date:
            event.add('dtstart', self.due_date.date)

        # recurring zettels should also have event_begin
        if 'recurring' in self and self.recurring:
            rrule = self.recurring

            if 'recurring_stop' in self and self.recurring_stop:
                rrule += f';until={self.recurring_stop.asRrule()}'

            event['rrule'] = parse_rrule(rrule)

        # Add duration.
        if 'duration' in self and self.duration:
            event.add('duration', parse_duration(self.duration))

        # Parse dtend
        if 'event_end' in self and self.event_end:
            event.add('dtend', self.event_end.date)

        return event

    @classmethod
    def createFromMd(cls, md):
        """ Create a new Zettel from markdown text.

        The text will be parsed to derive key-value zettels where the key
        is the heading and the value is the subsequent text.

        The title of the zettel is expected to be a markdown level-1 heading
        (# ) This is followed by the zettel's _notes, which is then
        succeeded by the rest of the zettel's headings, which are expected
        to be RST level 2 headings (## ).

        Args:
            md: Markdown text or filename from which to create the zettel.

        Returns:
            A new Zettel.

        Raises:
            ValueError if the markdown could not create a valid Zettel.
        """
        if os.path.exists(md):
            with open(md) as f:
                md = f.read()

        md = md.strip()
        if not md:
            raise ValueError('No text provided')

        ptr = 0

        title = ''
        headings = {}

        attr_header = '<!--- attributes --->'
        md = md.split(attr_header)
        if len(md) == 1:
            md.append('')

        # split out attributes and actual zettel text
        attributes = yaml.safe_load(md[-1].strip())
        md = attr_header.join(md[:-1]).splitlines()

        # Find the headings and content.
        heading_pts = [x for x, y in enumerate(md) if _is_md_heading(y)]

        # Find the title.
        if not heading_pts:
            raise ValueError('No title in zettel.')

        heading_pts.append(len(md))

        title = ' '.join(md[heading_pts[0]].split()[1:])

        # Gather _notes
        headings['_notes'] = '\n'.join(md[1:heading_pts[1]])

        # Get the rest
        for ptr in range(1, len(heading_pts) - 1):
            heading = ''.join(md[heading_pts[ptr]].split('##')[1:]).strip()
            content_start = heading_pts[ptr] + 1
            content_end = heading_pts[ptr + 1]
            headings[heading] = '\n'.join(md[content_start:content_end])

        return Zettel(title, headings, attributes)

    @classmethod
    def createFromRst(cls, rst):
        """ Create a new Zettel from RST text

        The title is expected to be an RST level-1 heading (=====). This
        is followed by the zettel's description.

        At the end of the description are the attributes. These are single
        line attributes which contain metadata about the zettel.

            ============================
             PROJ-77: My zettel's title
            ============================
            My zettels's description

            Other heading
            =============
            My other heading description

            .. attributes
            creator: OneRedDime
            assignee: OneRedDime
            creation_date: 03/01/2023

        Args:
            rst: RST-formatted text from which to create the zettel. This value
                be provided as a string of RST formatted text or a filename.

        Returns:
            A new Zettel.

        Raises:
            ValueError: If the RST could not create a valid Zettel.
        """
        if os.path.exists(rst):
            with open(rst) as f:
                rst = f.read()

        rst = rst.strip()
        if not rst:
            raise ValueError('No text provided')

        ptr = 0

        title = ''
        headings = {}

        # Split out the attributes and content.
        attr_header = '.. attributes\n::'
        rst = rst.split(attr_header)
        if len(rst) == 1:
            rst.append('')

        attributes = yaml.safe_load(rst[-1].strip())
        rst = attr_header.join(rst[:-1]).splitlines()

        # Strip the first line of === if it exists.
        if _is_rst_heading(rst[0]):
            rst = rst[1:]

        # Find the lines in the text that are heading markers.
        heading_pts = [x - 1 for x, y in enumerate(rst) if _is_rst_heading(y)]

        # First heading marker is the title.
        if not heading_pts or heading_pts[0] == -1:
            raise ValueError('No title in zettel.')

        heading_pts.append(len(rst))

        title = rst[heading_pts[0]].strip()

        # Gather _notes
        headings['_notes'] = '\n'.join(rst[heading_pts[0] + 2:heading_pts[1]])

        # Get the rest
        for ptr in range(1, len(heading_pts) - 1):
            heading = rst[heading_pts[ptr]]
            content_start = heading_pts[ptr] + 2
            content_end = heading_pts[ptr + 1]
            headings[heading] = '\n'.join(rst[content_start:content_end])

        return Zettel(title, headings, attributes)

    def refresh(self):
        """ Make minor corrections

        Tags should be sorted.
        """
        self.attrs['tags'] = sorted(list(set([x for x in self.attrs['tags']])))

    def update(self, new_zettel, exp_headings=None):
        """ Update a zettel.

        The title, headings, and attributes of this zettel will be
        replaced with the ones in new_zettel.

        If exp_headings=None, then it would be as if the whole body text
        is replaced.

        But if exp_headings is provided, then only those headings will be
        be expected to be in the new zettel. If one of those is missing
        then it will be deleted while others will be ignored.

        Args:
            new_zettel: Other zettel instance whose attributes will be used.
            exp_headings: If a heading is listed here, but is not found in
                the final text, then the heading will be deleted.

        Raises:
            See createFromRst.
        """
        exp_headings = exp_headings or []

        # Update this zettel.
        self.title = new_zettel.title

        self.attrs = Attributes()
        self.attrs.update(new_zettel.attrs)

        if not exp_headings:
            self.headings = new_zettel.headings
        else:
            for heading in exp_headings:
                if heading not in new_zettel.headings and heading in self.headings:
                    del(self.headings[heading])

            self.headings.update(new_zettel.headings)

        self.refresh()

    def getMd(self, headings=None):
        """ Display this zettel in MD format.

        Args:
            headings: Only display these headings.

        Returns:
            A markdown string representing the content of this zettel.
        """
        headings = headings or []
        headings = headings or self.headings
        headings = [x.lower() for x in headings]

        s = []
        s.append('# ' + self.title)

        if '_notes' in headings:
            s.append(self.headings['_notes'].rstrip())
            s.append('')

        # case-insensitive search
        lookup_headings = {k.lower(): k for k in self.headings}
        for heading in headings:
            if heading == '_notes' or heading not in lookup_headings:
                continue

            s.append('## ' + lookup_headings[heading])
            s.append(self.headings[lookup_headings[heading]].rstrip())
            s.append('')

        # Append the attributes
        s.append('<!--- attributes --->')
        s += ['    ' + x for x in str(self.attrs).splitlines()]
        s.append('')

        return '\n'.join(s)

    def getRst(self, headings=None):
        """ Display this zettel in RST format.

        Returns:
            An RST string representing the content of this zettel.
        """

        headings = headings or []
        headings = headings or self.headings
        headings = [x.lower() for x in headings]

        s = []
        s.append('=' * (len(self.title) + 2))
        s.append(' ' + self.title)
        s.append('=' * (len(self.title) + 2))

        if '_notes' in headings:
            s.append(self.headings['_notes'].rstrip())
            s.append('')

        # case-insensitive search
        lookup_headings = {k.lower(): k for k in self.headings}
        for heading in headings:
            if heading == '_notes' or heading not in lookup_headings:
                continue

            s.append(lookup_headings[heading])
            s.append('=' * len(lookup_headings[heading]))
            s.append(self.headings[lookup_headings[heading]].rstrip())
            s.append('')

        # Append the attributes
        s.append('.. attributes')
        s.append('::')
        s.append('')
        s += ['    ' + x for x in str(self.attrs).splitlines()]

        # Will become trailing newline
        s.append('')

        return '\n'.join(s)
