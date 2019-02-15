# coding=utf-8
"""BlockMeshDict class."""
from .foamfile import FoamFile, foam_file_from_file
from .functions import Function
from collections import OrderedDict


class ControlDict(FoamFile):
    """Control dict class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['#include'] = None
    # application will be updated based on recipe
    __default_values['application'] = None
    __default_values['startFrom'] = 'latestTime'
    __default_values['startTime'] = '0'
    __default_values['stopAt'] = 'endTime'
    __default_values['endTime'] = '1000'
    __default_values['deltaT'] = '1'
    __default_values['writeControl'] = 'timeStep'
    __default_values['writeInterval'] = '100'
    __default_values['purgeWrite'] = '0'
    __default_values['writeFormat'] = 'ascii'
    __default_values['writePrecision'] = '8'
    __default_values['writeCompression'] = 'off'
    __default_values['timeFormat'] = 'general'
    __default_values['timePrecision'] = '6'
    __default_values['runTimeModifiable'] = 'true'
    __default_values['functions'] = OrderedDict()

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='controlDict', cls='dictionary',
                          location='system', default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @property
    def include(self):
        """Get if any file is included in controlDict."""
        return self.values['#include']

    @include.setter
    def include(self, file_name):
        """Add include to controlDict."""
        self.values['#include'] = '"{}"'.format(file_name.replace('"', ''))

    @property
    def application(self):
        """Set solver application.

        (default: simpleFoam)
        """
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
    def purgeWrite(self):
        """Set the number of results folders to be kept (default: 0)."""
        return self.values['purgeWrite']

    @purgeWrite.setter
    def purgeWrite(self, value=0):
        self.values['purgeWrite'] = str(int(value))

    @property
    def writeCompression(self):
        """Write results as .zip files.

        Set to True to compress the results before writing to your machine
        (default: False)
        """
        return self.values['writeCompression']

    @writeCompression.setter
    def writeCompression(self, value=True):
        self.values['writeCompression'] = self.convert_bool_value(value)

    @property
    def functions(self):
        """Function objects."""
        self.values['functions']

    @functions.setter
    def functions(self, func_objects):
        fos = (f if hasattr(f, 'isFunction') else Function.from_cpp_dictionary(f)
               for f in func_objects)
        self.values['functions'] = OrderedDict()
        for f in fos:
            self.values['functions'].update(f.values)
