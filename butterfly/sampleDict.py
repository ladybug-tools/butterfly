# coding=utf-8
"""sampleDict class."""
from foamfile import Condition, foam_file_from_file
from collections import OrderedDict


class SampleDict(Condition):
    """Probes function."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['libs'] = '("libsampling.so")'
    __default_values['interpolationScheme'] = 'cellPoint'
    __default_values['setFormat'] = 'raw'
    __default_values['type'] = 'sets'
    __default_values['fields'] = '(p U)'  # Fields
    __default_values['sets'] = OrderedDict()

    def __init__(self, values=None):
        """Init class."""
        super(SampleDict, self).__init__(
            name='sampleDict', cls='dictionary', location='system',
            default_values=self.__default_values, values=values
        )
        self._pts = None
        self._name = None
        self.filename = 'sampleName'

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        _cls = cls(values=foam_file_from_file(filepath, cls.__name__))
        return _cls

    @classmethod
    def from_points(cls, name, points, fields):
        """Create sampleDict from points and fields."""
        cls_ = cls()
        cls_.filename = name
        cls_.points = points
        cls_.fields = fields
        return cls_

    @property
    def points_count(self):
        """Get number of probes."""
        if not self.points:
            return 0
        else:
            return len(' '.join(self.points)[1:-1].split(')')) - 1

    @property
    def output_filenames(self):
        """A tuple of output file names."""
        return tuple('{}_{}.xy'.format(self.filename, f) for f in self.fields)

    @property
    def points(self):
        """Get and set probe locations from list of tuples."""
        return self._pts

    @points.setter
    def points(self, pts):
        self._pts = tuple(str(tuple(pt)).replace(',', ' ') for pt in pts)
        self.values['sets'][self._name]['points'] = '({})'.format(' '.join(self._pts))

    @property
    def filename(self):
        """Get SampleDict filename."""
        return self._name

    @filename.setter
    def filename(self, n):
        """Set SampleDict filename."""
        if not n:
            return
        if self._name in self.values['sets']:
            del(self.values['sets'][self._name])
        self._name = str(n)
        self.values['sets'][self._name] = OrderedDict()
        self.values['sets'][self._name]['type'] = 'cloud'
        self.values['sets'][self._name]['axis'] = 'xyz'
        if self._pts:
            self.values['sets'][self._name]['points'] = \
                '({})'.format(' '.join(self._pts))

    @property
    def fields(self):
        """Get and set probes fields from list of tuples."""
        return self.values['fields'] \
            .replace('(', '').replace(')', '').split()

    @fields.setter
    def fields(self, fields_list):
        if not fields_list:
            return
        self.values['fields'] = \
            str(tuple(fields_list)).replace(',', ' ') \
            .replace("'", '').replace('"', '') \
            .replace("\\r", '').replace("\\n", ' ')

    def save(self, project_folder, sub_folder=None):
        """Save sampleDict file.

        The file will be named
        """
        if self.points_count == 0:
            return
        else:
            fp = super(SampleDict, self).save(project_folder, sub_folder)
            # update the sets{} for sets();
            # This is quite hacky but will work
            with open(fp, 'rb') as inf:
                f = inf.read()
            ff = f.replace('sets\n{', 'sets\n(')[:-1] + ');\n'
            with open(fp, 'wb') as outf:
                outf.write(ff)
            return fp
