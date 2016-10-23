# coding=utf-8
"""U class."""
from foamfile import FoamFileZeroFolder, foamFileFromFile
from collections import OrderedDict


class U(FoamFileZeroFolder):
    """U (Speed) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 1 -1 0 0 0 0]'
    __defaultValues['#include'] = None
    __defaultValues['internalField'] = 'uniform (0 0 0)'
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFileZeroFolder.__init__(self, name='U', cls='volVectorField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))
