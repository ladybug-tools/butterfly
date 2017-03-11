# coding=utf-8
"""TransportProperties class."""
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class TransportProperties(FoamFile):
    """Transport Properties class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['transportModel'] = 'Newtonian'
    __defaultValues['nu'] = 'nu [0 2 -1 0 0 0 0] 1e-05'
    __defaultValues['beta'] = 'beta [0 0 0 -1 0 0 0] 3e-03'
    __defaultValues['TRef'] = 'TRef [0 0 0 1 0 0 0] 300'
    __defaultValues['Pr'] = 'Pr [0 0 0 0 0 0 0] 0.9'
    __defaultValues['Prt'] = 'Prt [0 0 0 0 0 0 0] 0.7'
    __defaultValues['Cp0'] = '1000'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='transportProperties', cls='dictionary',
                          location='constant', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))
