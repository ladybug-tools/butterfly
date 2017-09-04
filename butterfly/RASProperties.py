# coding=utf-8
"""RASProperties class.

Use turbulence_properties from Version 3.0+
"""
from foamfile import FoamFile, foam_file_from_file
from collections import OrderedDict


class RASProperties(FoamFile):
    """Finite Volume Solution class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['RASModel'] = 'kEpsilon'
    __default_values['turbulence'] = 'on'
    __default_values['printCoeffs'] = 'on'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='RASProperties', cls='dictionary',
                          location='constant', default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))
