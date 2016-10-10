# coding=utf-8
"""alphat class."""
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict


class Alphat(ZeroFolderFoamFile):
    """alphat class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 2 -1 0 0 0 0]'
    __defaultValues['internalField'] = 'uniform 0'
    __defaultValues['boundaryField'] = None

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='alphat',
                                    cls='volScalarField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)
