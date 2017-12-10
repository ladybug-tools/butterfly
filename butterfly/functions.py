# coding=utf-8
"""A cllection of OpenFOAM functions such as Probes."""
from .foamfile import FoamFile, foam_file_from_file
from .parser import CppDictParser
from collections import OrderedDict


class Function(FoamFile):
    """OpenFOAM function object.

    Use this class to create conditions function objects.
    Functions don't have OpenFOAM header and OpenFOAM FoamFile. It's only values.
    """

    @classmethod
    def from_cpp_dictionary(cls, dictionary):
        """Create a foamfile from an OpenFOAM dictionary in text format."""
        # convert values to python dictionary
        values = CppDictParser(text=dictionary).values

        if 'FoamFile' in values:
            del(values['FoamFile'])

        assert len(values.keys()) == 1, \
            """You can define one function object at a time."""

        return cls(values.keys()[0], 'dictionary', values=values)

    def header(self):
        """Return conditions header."""
        return ''

    def __repr__(self):
        """Object representation."""
        return 'Function Object: {}'.format(self.name)


class Probes(Function):
    """Probes function."""

    # set default valus for this class
    __default_values = {'functions': {'probes': OrderedDict()}}
    __default_values['functions']['probes']['functionObjectLibs'] = '("libsampling.so")'
    __default_values['functions']['probes']['type'] = 'probes'
    __default_values['functions']['probes']['name'] = 'probes'
    __default_values['functions']['probes']['fields'] = '(p U)'  # Fields to be probed
    __default_values['functions']['probes']['probeLocations'] = None
    __default_values['functions']['probes']['writeControl'] = 'timeStep'
    __default_values['functions']['probes']['writeInterval'] = '1'

    def __init__(self, values=None):
        """Init class."""
        super(Probes, self).__init__(
            name='probes', cls='dictionary', location='system',
            default_values=self.__default_values, values=values
        )

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        _cls = cls(values=foam_file_from_file(filepath, cls.__name__))
        return _cls

    @property
    def probes_count(self):
        """Get number of probes."""
        if not self.probeLocations:
            return 0
        else:
            return len(self.probeLocations[1:-1].split(')')) - 1

    @property
    def probeLocations(self):
        """Get and set probe locations from list of tuples."""
        return self.values['functions']['probes']['probeLocations']

    @probeLocations.setter
    def probeLocations(self, pts):
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
    def fields(self, fields_list):
        if not fields_list:
            return
        self.values['functions']['probes']['fields'] = \
            str(tuple(fields_list)).replace(',', ' ') \
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

    def save(self, project_folder, sub_folder=None):
        if self.probes_count == 0:
            return
        else:
            super(Probes, self).save(project_folder, sub_folder)

    def __repr__(self):
        """Class representation."""
        return self.to_openfoam()
