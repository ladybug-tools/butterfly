# coding=utf-8
"""epsilon class."""
from foamfile import FoamFileZeroFolder, foam_file_from_file
from collections import OrderedDict


class Epsilon(FoamFileZeroFolder):
    """epsilon class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['dimensions'] = '[0 2 -3 0 0 0 0]'
    __default_values['#include'] = None
    __default_values['internalField'] = 'uniform 0.01'
    __default_values['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFileZeroFolder.__init__(self, name='epsilon', cls='volScalarField',
                                    location='0',
                                    default_values=self.__default_values,
                                    values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @property
    def dimensions(self):
        """Return dimensions."""
        return self.values['dimensions']

    @property
    def internalField(self):
        """Return internalField."""
        return self.values['internalField']

    @internalField.setter
    def internalField(self, v):
        """set internalField value."""
        self.values['internalField'] = v
