"BlockMeshDict class."
from foamfile import FoamFile
from collections import OrderedDict

class ControlDict(FoamFile):
    """Control dict class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['#include'] = None
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

    def include(self, fileName):
        "Add include to controlDict."
        self.values['#include'] = '"{}"'.format(fileName.replace('"', ''))

    @property
    def application(self):
        """Set solver application (default: simpleFoam)."""
        return self.values['application']

    @application.setter
    def application(self, value='simpleFoam'):
        self.values['application'] = str(value)

    @property
    def startTime(self):
        """Set start timestep (default: 0)."""
        return self.values['startTime']

    @startTime.setter
    def startTime(self, value=0):
        self.values['startTime'] = str(int(value))

    @property
    def endTime(self):
        """Set end timestep (default: 1000)."""
        return self.values['endTime']

    @endTime.setter
    def endTime(self, value=0):
        self.values['endTime'] = str(int(value))

    @property
    def writeInterval(self):
        """Set the number of intervals for writing the results (default: 100)."""
        return self.values['writeInterval']

    @writeInterval.setter
    def writeInterval(self, value=100):
        self.values['writeInterval'] = str(int(value))

    @property
    def writeCompression(self):
        """Write results as .zip files.

        Set to True to compress the results before writing to your machine
        (default: False)
        """
        return self.values['writeCompression']

    @writeCompression.setter
    def writeCompression(self, value=True):
        self.values['writeCompression'] = str(bool(value)).lower()
