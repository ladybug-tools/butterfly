"""turbulenceProperties class.

Use turbulenceProperties for versions prior to 3.0+
"""
from foamfile import FoamFile
from collections import OrderedDict


# TODO: Add other turbulence models
class TurbulenceProperties(FoamFile):
    """Turbulence Properties class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['simulationType'] = 'RAS'
    __defaultValues['RAS'] = {
        'RASModel': 'kEpsilon',
        'turbulence': 'on',
        'printCoeffs': 'on'
    }

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='turbulenceProperties', cls='dictionary',
                          location='constant', defaultValues=self.__defaultValues,
                          values=values)
