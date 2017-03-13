# coding=utf-8
"""decomposeParDict class.

Decompose parameters for parallel runs.
"""
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class DecomposeParDict(FoamFile):
    """DecomposeParDict class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['numberOfSubdomains'] = '2'
    __defaultValues['method'] = 'scotch'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='decomposeParDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

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
    def simple(cls, numberOfSubdomainsXYZ=None, delta=0.001):
        """Simple method.

        Args:
            numberOfSubdomainsXYZ: Number of subdomains in x, y, z as a tuple
                (default: (2, 1, 1))
            delta: Cell skew factor (default: 0.001).
        """
        try:
            numberOfSubdomainsXYZ = tuple(numberOfSubdomainsXYZ)
        except Exception:
            numberOfSubdomainsXYZ = (2, 1, 1)

        numberOfSubdomains = numberOfSubdomainsXYZ[0] * \
            numberOfSubdomainsXYZ[1] * numberOfSubdomainsXYZ[2]

        values = {'method': 'simple',
                  'numberOfSubdomains': str(numberOfSubdomains),
                  'simpleCoeffs':
                  {'n': str(numberOfSubdomainsXYZ).replace(',', ' '),
                   'delta': str(delta)}}

        return cls(values=values)
