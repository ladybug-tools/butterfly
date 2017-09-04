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
    def number_of_subdomains(self):
        """Get number of total subdomains."""
        return self.values['numberOfSubdomains']

    @classmethod
    def scotch(cls, number_of_subdomains=2):
        """Scotch method.

        Args:
            number_of_subdomains: Total number of subdomains (default: 2).
        """
        values = {'method': 'scotch',
                  'numberOfSubdomains': str(number_of_subdomains)}
        return cls(values=values)

    @classmethod
    def simple(cls, number_of_subdomains_xyz=None, delta=0.001):
        """Simple method.

        Args:
            number_of_subdomains_xyz: Number of subdomains in x, y, z as a tuple
                (default: (2, 1, 1))
            delta: Cell skew factor (default: 0.001).
        """
        try:
            number_of_subdomains_xyz = tuple(number_of_subdomains_xyz)
        except Exception:
            number_of_subdomains_xyz = (2, 1, 1)

        number_of_subdomains = number_of_subdomains_xyz[0] * \
            number_of_subdomains_xyz[1] * number_of_subdomains_xyz[2]

        values = {'method': 'simple',
                  'numberOfSubdomains': str(number_of_subdomains),
                  'simpleCoeffs':
                  {'n': str(number_of_subdomains_xyz).replace(',', ' '),
                   'delta': str(delta)}}

        return cls(values=values)
