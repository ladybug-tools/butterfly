"epsilon class."
from foamfile import FoamFile
from collections import OrderedDict


class Epsilon(FoamFile):
    """epsilon class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 2 -3 0 0 0 0]'
    __defaultValues['internalField'] = 'uniform 0.01'
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='epsilon', cls='volScalarField',
                          location='0', defaultValues=self.__defaultValues,
                          values=values)

fv = Epsilon()
fv.save(r'C:\Users\Administrator\butterfly\innerflow_3')
