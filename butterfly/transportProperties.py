# coding=utf-8
"""TransportProperties class."""
from foamfile import FoamFile, foam_file_from_file
from collections import OrderedDict


class TransportProperties(FoamFile):
    """Transport Properties class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['transportModel'] = 'Newtonian'
    __default_values['nu'] = 'nu [0 2 -1 0 0 0 0] 1e-05'
    __default_values['beta'] = 'beta [0 0 0 -1 0 0 0] 3e-03'
    __default_values['TRef'] = 't_ref [0 0 0 1 0 0 0] 300'
    __default_values['Pr'] = 'Pr [0 0 0 0 0 0 0] 0.9'
    __default_values['Prt'] = 'prt [0 0 0 0 0 0 0] 0.7'
    __default_values['Cp0'] = '1000'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='transport_properties', cls='dictionary',
                          location='constant', default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))
