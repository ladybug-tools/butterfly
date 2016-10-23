# coding=utf-8
"""p_rgh class."""
from foamfile import FoamFileZeroFolder, foamFileFromFile
from collections import OrderedDict


class P_rgh(FoamFileZeroFolder):
    """p_rgh class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 2 -2 0 0 0 0]'
    __defaultValues['internalField'] = 'uniform 0'
    __defaultValues['boundaryField'] = None

    def __init__(self, values=None):
        """Init class."""
        FoamFileZeroFolder.__init__(self, name='p_rgh',
                                    cls='volScalarField',
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
