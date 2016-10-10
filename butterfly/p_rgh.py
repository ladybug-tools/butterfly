# coding=utf-8
"""p_rgh class."""
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict


class P_rgh(ZeroFolderFoamFile):
    """p_rgh class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 2 -2 0 0 0 0]'
    __defaultValues['internalField'] = 'uniform 0'
    __defaultValues['boundaryField'] = None

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='p_rgh',
                                    cls='volScalarField',
                                    location='0',
                                    defaultValues=self.__defaultValues,
                                    values=values)
