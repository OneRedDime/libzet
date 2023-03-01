import yaml

from superdate import SuperDate

from libzet.NoCompare import NoCompare


class Attributes(dict):
    """ Class to hold a Zettel's attributes.

    If a non-existent attribute is queried then a NoCompare is returned.

    This class also allows getting items in the dict via the dot operator.
    This means keys in this dict must be valid python3 identifiers.
    """
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    @classmethod
    def fromYaml(cls, s):
        """ Load Attributes from yaml.

        Args:
            s: String or filename of yaml to init from.
        Raises:
            FileNotFoundError or PermissionError if yaml was a file and
                couldn't be read.

            Whatever yaml.safe_load raises.
        """
        d = yaml.safe_load(s)
        if type(d) is str:
            with open(s) as f:
                s = f.read()
            d = yaml.safe_load(s)

        return Attributes(d)

    def toYamlDict(self):
        """ Reverses SuperDate to easymode yaml str.

        Necessary to dump this object as a yaml string.

            yaml.dump(attributes.toYamlDict)

        Returns:
            A dictionary that yaml can dump.
        """
        d = dict()
        d.update(self)
        dtfields = ['event_begin', 'event_end', 'recurring_stop']

        for k, v in d.items():
            if v and (k in dtfields or 'date' in k):
                d[k] = v.strftime('%Y-%m-%d, %a')

        return d

    def __str__(self):
        return '---\n' + yaml.dump(self.toYamlDict())

    def __getattr__(self, key):
        """ Expose keys as attributes.
        """
        if key in self.__dict__:
            return self.__dict__[key]

        return self.__getitem__(key)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return NoCompare()

    def __setitem__(self, key, val):
        """ Keys must be python3 identifiers.

        Will also perform special parsing logic for keys that contain
        the word "date".
        """
        try:
            if not key.isidentifier():
                raise ValueError(f'The key "{key}" is not a valid identifier.')
        except AttributeError as ae:
            raise ValueError('Keys must be strings')

        dtfields = ['event_begin', 'event_end', 'recurring_stop']
        if val and (key in dtfields or 'date' in key):
            val = SuperDate(val)

        dict.__setitem__(self, key, val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
