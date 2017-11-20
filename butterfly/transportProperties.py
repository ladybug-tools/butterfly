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
    __default_values['TRef'] = 'TRef [0 0 0 1 0 0 0] 300'
    __default_values['Pr'] = 'Pr [0 0 0 0 0 0 0] 0.9'
    __default_values['Prt'] = 'Prt [0 0 0 0 0 0 0] 0.7'
    __default_values['Cp0'] = '1000'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='transportProperties', cls='dictionary',
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
    def transportModel(self):
        return self.values['transportModel']

    @property
    def nu(self):
        return self.values['nu']

    @property
    def beta(self):
        return self.values['beta']

    @property
    def TRef(self):
        return self.values['TRef']

    @property
    def Pr(self):
        return self.values['Pr']

    @property
    def Prt(self):
        return self.values['Prt']

    @property
    def Cp0(self):
        return self.values['Cp0']
