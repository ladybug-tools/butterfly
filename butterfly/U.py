"BlockMeshDict class."
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict


class U(ZeroFolderFoamFile):
    """U (Speed) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 1 -1 0 0 0 0]'
    __defaultValues['#include'] = None
    __defaultValues['internalField'] = None
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='U', cls='volVectorField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)