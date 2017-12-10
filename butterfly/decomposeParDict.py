# coding=utf-8
"""decomposeParDict class.

Decompose parameters for parallel runs.
"""
from foamfile import FoamFile, foam_file_from_file
from collections import OrderedDict


class DecomposeParDict(FoamFile):
    """DecomposeParDict class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['numberOfSubdomains'] = '2'
    __default_values['method'] = 'scotch'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='decomposeParDict', cls='dictionary',
                          location='system', default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @property
    def numberOfSubdomains(self):
        """Get number of total subdomains."""
        return self.values['numberOfSubdomains']

    @classmethod
    def scotch(cls, numberOfSubdomains=2):
        """Scotch method.

        Args:
            numberOfSubdomains: Total number of subdomains (default: 2).
        """
        values = {'method': 'scotch',
                  'numberOfSubdomains': str(numberOfSubdomains)}
        return cls(values=values)

    @classmethod
    def simple(cls, numberOfSubdomains_xyz=None, delta=0.001):
        """Simple method.

        Args:
            numberOfSubdomains_xyz: Number of subdomains in x, y, z as a tuple
                (default: (2, 1, 1))
            delta: Cell skew factor (default: 0.001).
        """
        try:
            numberOfSubdomains_xyz = tuple(numberOfSubdomains_xyz)
        except Exception:
            numberOfSubdomains_xyz = (2, 1, 1)

        numberOfSubdomains = numberOfSubdomains_xyz[0] * \
            numberOfSubdomains_xyz[1] * numberOfSubdomains_xyz[2]

        values = {'method': 'simple',
                  'numberOfSubdomains': str(numberOfSubdomains),
                  'simpleCoeffs':
                  {'n': str(numberOfSubdomains_xyz).replace(',', ' '),
                   'delta': str(delta)}}

        return cls(values=values)
