# coding=utf-8
"""sampleDict class."""
from foamfile import Condition, foamFileFromFile
from collections import OrderedDict


class SampleDict(Condition):
    """Probes function."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['libs'] = '("libsampling.so")'
    __defaultValues['interpolationScheme'] = 'cellPoint'
    __defaultValues['setFormat'] = 'raw'
    __defaultValues['type'] = 'sets'
    __defaultValues['fields'] = '(p U)'  # Fields
    __defaultValues['sets'] = OrderedDict()

    def __init__(self, values=None):
        """Init class."""
        super(SampleDict, self).__init__(
            name='sampleDict', cls='dictionary', location='system',
            defaultValues=self.__defaultValues, values=values
        )
        self._pts = None
        self._name = None
        self.filename = 'sampleName'

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        _cls = cls(values=foamFileFromFile(filepath, cls.__name__))
        return _cls

    @classmethod
    def fromPoints(cls, name, points, fields):
        """Create sampleDict from points and fields."""
        cls_ = cls()
        cls_.filename = name
        cls_.points = points
        cls_.fields = fields
        return cls_

    @property
    def pointsCount(self):
        """Get number of probes."""
        if not self.points:
            return 0
        else:
            return len(' '.join(self.points)[1:-1].split(')')) - 1

    @property
    def outputFilenames(self):
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
    def fields(self, fieldsList):
        if not fieldsList:
            return
        self.values['fields'] = \
            str(tuple(fieldsList)).replace(',', ' ') \
            .replace("'", '').replace('"', '') \
            .replace("\\r", '').replace("\\n", ' ')

    def save(self, projectFolder, subFolder=None):
        """Save sampleDict file.

        The file will be named
        """
        if self.pointsCount == 0:
            return
        else:
            fp = super(SampleDict, self).save(projectFolder, subFolder)
            # update the sets{} for sets();
            # This is quite hacky but will work
            with open(fp, 'rb') as inf:
                f = inf.read()
            ff = f.replace('sets\n{', 'sets\n(')[:-1] + ');\n'
            with open(fp, 'wb') as outf:
                outf.write(ff)
            return fp
