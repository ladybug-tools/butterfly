# coding=utf-8
"""g[ravity] class."""
from foamfile import ZeroFolderFoamFile
from collections import OrderedDict


class G(ZeroFolderFoamFile):
    """G (gravity) class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['dimensions'] = '[0 1 -2 0 0 0 0]'
    __defaultValues['#include'] = None
    __defaultValues['value'] = '(0 0 -9.81)'

    def __init__(self, values=None):
        """Init class."""
        ZeroFolderFoamFile.__init__(self, name='g',
                                    cls='uniformDimensionedVectorField',
                                    location='constant',
                                    defaultValues=self.__defaultValues,
                                    values=values)
