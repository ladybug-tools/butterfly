# coding=utf-8
"""p_rgh class."""
from foamfile import FoamFileZeroFolder, foam_file_from_file
from collections import OrderedDict


class P_rgh(FoamFileZeroFolder):
    """p_rgh class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['dimensions'] = '[0 2 -2 0 0 0 0]'
    __default_values['internalField'] = 'uniform 0'
    __default_values['boundaryField'] = None

    def __init__(self, values=None):
        """Init class."""
        FoamFileZeroFolder.__init__(self, name='p_rgh',
                                    cls='volScalarField',
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
