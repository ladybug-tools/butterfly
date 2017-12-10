# coding=utf-8
"""RASProperties class.

Use turbulenceProperties from Version 3.0+
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

    @property
    def RASModel(self):
        """RAS model."""
        return self.values['RASModel']

    @property
    def turbulence(self):
        """is turbulence on/off."""
        return self.values['turbulence']

    @turbulence.setter
    def turbulence(self, is_turbulence=True):
        """is turbulence on/off."""
        if is_turbulence:
            self.values['turbulence'] = 'on'
        else:
            self.values['turbulence'] = 'off'

    @property
    def printCoeffs(self):
        """is printCoeffs on/off."""
        return self.values['printCoeffs']

    @printCoeffs.setter
    def printCoeffs(self, is_printCoeffs=True):
        """is printCoeffs on/off."""
        if is_printCoeffs:
            self.values['printCoeffs'] = 'on'
        else:
            self.values['printCoeffs'] = 'off'
