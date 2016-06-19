"BlockMeshDict class."
from foamfile import FoamFile
from collections import OrderedDict

class ControlDict(FoamFile):
    """Control dict class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['application'] = 'simpleFoam'
    __defaultValues['startFrom'] = 'latestTime'
    __defaultValues['startTime'] = '0'
    __defaultValues['stopAt'] = 'endTime'
    __defaultValues['endTime'] = '1000'
    __defaultValues['deltaT'] = '1'
    __defaultValues['writeControl'] = 'timeStep'
    __defaultValues['writeInterval'] = '100'
    __defaultValues['purgeWrite'] = '0'
    __defaultValues['writeFormat'] = 'ascii'
    __defaultValues['writePrecision'] = '6'
    __defaultValues['writeCompression'] = 'off'
    __defaultValues['timeFormat'] = 'general'
    __defaultValues['timePrecision'] = '6'
    __defaultValues['runTimeModifiable'] = 'true'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='controlDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)
