# coding=utf-8
"""RASProperties class.

Use turbulenceProperties from Version 3.0+
"""
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class RASProperties(FoamFile):
    """Finite Volume Solution class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['RASModel'] = 'kEpsilon'
    __defaultValues['turbulence'] = 'on'
    __defaultValues['printCoeffs'] = 'on'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='RASProperties', cls='dictionary',
                          location='constant', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))
