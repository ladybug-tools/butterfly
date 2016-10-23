# coding=utf-8
"""A cllection of OpenFOAM functions such as Probes."""
from foamfile import Condition, foamFileFromFile
from collections import OrderedDict


class Probes(Condition):
    """Probes function."""

    # set default valus for this class
    __defaultValues = {'functions': {'probes': OrderedDict()}}
    __defaultValues['functions']['probes']['functionObjectLibs'] = '("libsampling.so")'
    __defaultValues['functions']['probes']['type'] = 'probes'
    __defaultValues['functions']['probes']['name'] = 'probes'  # name of the directory for probe data
    __defaultValues['functions']['probes']['fields'] = '(p U)'  # Fields to be probed
    __defaultValues['functions']['probes']['probeLocations'] = None  # locations as (x y z)
    __defaultValues['functions']['probes']['writeControl'] = 'timeStep'
    __defaultValues['functions']['probes']['writeInterval'] = '1'

    def __init__(self, values=None):
        """Init class."""
        self.__count = 0
        super(Probes, self).__init__(
            name='probes', cls='dictionary', location='system',
            defaultValues=self.__defaultValues, values=values
        )

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    @property
    def probesCount(self):
        """Get number of probes."""
        return self.__count

    @property
    def probeLocations(self):
        """Get and set probe locations from list of tuples."""
        return self.values['functions']['probes']['probeLocations']

    @probeLocations.setter
    def probeLocations(self, pts):
        self.__count = len(pts)
        ptlist = (str(tuple(pt)).replace(',', ' ') for pt in pts)
        self.values['functions']['probes']['probeLocations'] = \
            '({})'.format(' '.join(ptlist))

    @property
    def filename(self):
        """Get Probes filename."""
        return self.values['functions']['probes']['name']

    @filename.setter
    def filename(self, n):
        """Set Probes filename."""
        if not n:
            return

        self.values['functions']['probes']['name'] = str(n)

    @property
    def fields(self):
        """Get and set probes fields from list of tuples."""
        return self.values['functions']['probes']['fields'] \
            .replace('(', '').replace(')', '').split()

    @fields.setter
    def fields(self, fieldsList):
        if not fieldsList:
            return
        self.values['functions']['probes']['fields'] = \
            str(tuple(fieldsList)).replace(',', ' ') \
            .replace("'", '').replace('"', '') \
            .replace("\\r", '').replace("\\n", ' ')

    @property
    def writeInterval(self):
        """Set the number of intervals for writing the results (default: 100)."""
        return self.values['functions']['probes']['writeInterval']

    @writeInterval.setter
    def writeInterval(self, value):
        if not value:
            return
        self.values['functions']['probes']['writeInterval'] = str(int(value))
