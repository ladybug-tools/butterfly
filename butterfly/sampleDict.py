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
    __defaultValues['setFormat'] = 'raw'  # name of the directory for probe data
    __defaultValues['type'] = 'sets'
    __defaultValues['fields'] = '(p U)'  # Fields to be probed
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

    @property
    def pointsCount(self):
        """Get number of probes."""
        if not self.points:
            return 0
        else:
            return len(' '.join(self.points)[1:-1].split(')')) - 1

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
        """Get Probes filename."""
        return self._name

    @filename.setter
    def filename(self, n):
        """Set Probes filename."""
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
        """Save sampleDict file."""
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
