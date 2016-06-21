"BlockMeshDict class."
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict

class U(ZeroFolderFoamFile):
    """U (Speed) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = 'nu [0 2 -1 0 0 0 0] 1e-05'
    __defaultValues['internalField'] = 'beta [0 0 0 -1 0 0 0] 3e-03'
    __defaultValues['boundaryField'] = {}

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='U', cls='volVectorField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)

    @classmethod
    def fromBFSurfaces(cls, BFSurfaces, values=None):
        """Init class by BFSurfaces."""
        _cls = cls(values)
        _cls.setBoundaryField(BFSurfaces)
        return _cls
