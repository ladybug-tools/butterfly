# coding=utf-8
"""T[emperature] class."""
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict


class T(ZeroFolderFoamFile):
    """T (temperature) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 0 0 1 0 0 0]'
    # default value which should be overwritten.
    __defaultValues['internalField'] = 'uniform 300'
    __defaultValues['boundaryField'] = None

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='T',
                                    cls='volScalarField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)
