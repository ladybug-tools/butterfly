"k class."
from foamfile import FoamFile
from collections import OrderedDict


class K(FoamFile):
    """k class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 2 -2 0 0 0 0]'
    __defaultValues['internalField'] = 'uniform 0.1'
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='k', cls='volScalarField',
                          location='0', defaultValues=self.__defaultValues,
                          values=values)

# fv = K()
# fv.save(r'C:\Users\Administrator\butterfly\innerflow_3')
