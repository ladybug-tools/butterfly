# coding=utf-8
"""Foam File Class."""
from .version import Version, Header
from .helper import getBoundaryField
from .parser import CppDictParser
import os
import json
from collections import OrderedDict
from copy import deepcopy


class FoamFile(object):
    """FoamFile base class for OpenFOAM dictionaries.

    Read (http://cfd.direct/openfoam/user-guide/basic-file-format/) for
    more information about FoamFile

    Attributes:
        name: Filename (e.g. controlDict)
        OFClass: OpenFOAM class constructed from the data file
            concerned. Typically  dictionary  or a field, e.g. volVectorField
        location: Folder name (0, constant or system)
        fileFormat: File format (ascii / binary) (default: ascii)
    """

    __locations = ('0', 'system', 'constant')

    def __init__(self, name, cls, location=None, fileFormat="ascii",
                 defaultValues=None, values=None):
        """Init foam file."""
        self.__version = str(Version().OFVer)
        self.format = str(fileFormat)  # ascii / binary
        self.cls = str(cls)  # dictionary or field
        self.name = str(name)
        self.location = location  # location is optional

        if self.location:
            if self.location.replace('"', '') in self.__locations:
                self.location = '"' + self.location.replace('"', '') + '"'
            else:
                    raise ValueError(
                        '{} is not a valid OpenFOAM location: {}'.format(
                            self.location, self.__locations
                        )
                    )

        # Initiate values
        if not values:
            values = {}
        if not defaultValues:
            defaultValues = {}
        self.__values = deepcopy(defaultValues)
        self.updateValues(values)

    @classmethod
    def fromFile(cls, filepath, location=None):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
            location: Optional folder name for location (0, constant or system)
        """
        def _tryGetFoamFileValue(key):
            try:
                return _values['FoamFile'][key]
            except KeyError:
                print 'failed to find {} in file. Using default velue: {}' \
                    .format(key, default[key])
                return default[key]

        _values = CppDictParser.fromFile(filepath).values
        p, _name = os.path.split(filepath)

        default = {
            'object': _name,
            'class': 'dictionary',
            'location': None,
            'format': 'ascii'
        }

        # set up FoamFile dictionary
        _name = _tryGetFoamFileValue('object')
        _cls = _tryGetFoamFileValue('class')
        _location = _tryGetFoamFileValue('location')
        _fileFormat = _tryGetFoamFileValue('format')

        if 'FoamFile' in _values:
            del(_values['FoamFile'])

        return cls(_name, _cls, _location, _fileFormat, values=_values)

    @property
    def values(self):
        """Return values as a dictionary."""
        return self.__values

    def updateValues(self, v):
        """Update current values from dictionary v.

        if key is not available in current values it will be added, if the key
        already exists it will be updated.

        Returns:
            True is the dictionary is updated.
        """
        def compare(d):
            """compare this dictionary with the current values."""
            for key, value in d.items():
                if isinstance(value, dict):
                    compare(value)
                if key not in self.__values:
                    # there is a new key so dictionary has changed.
                    return True
                else:
                    if str(self.__values[key]) != str(value):
                        # there is a change in value
                        return True
            return False

        assert isinstance(v, dict), 'Expected dictionary not {}!'.format(type(v))

        if compare(v):
            self.__values.update(v)
            return True
        else:
            return False

    @property
    def parameters(self):
        """Get list of parameters."""
        return self.values.keys()

    def getValueByParameter(self, parameter):
        """Get values for a given parameter by parameter name.

        Args:
            parameter: Name of a parameter as a string.
        """
        try:
            return self.values[parameter]
        except KeyError:
            raise KeyError('{} is not available in {}.'.format(
                parameter, self.__class__.__name__
            ))

    def setValueByParameter(self, parameter, value):
        """Set value for a parameter.

        Args:
            parameter: Name of a parameter as a string.
            value: Parameter value as a string.
        """
        self.values[parameter] = value

    def header(self):
        """Return open foam style string."""
        if self.location:
            return Header.header() + \
                "FoamFile\n{\n" \
                "\tversion\t\t%s;\n" \
                "\tformat\t\t%s;\n" \
                "\tclass\t\t%s;\n" \
                "\tlocation\t%s;\n" \
                "\tobject\t\t%s;\n" \
                "}\n" % (self.__version, self.format, self.cls, self.location,
                         self.name)
        else:
            return Header.header() + \
                "FoamFile\n{\n" \
                "\tversion\t\t%s;\n" \
                "\tformat\t\t%s;\n" \
                "\tclass\t\t%s;\n" \
                "\tobject\t\t%s;\n" \
                "}\n" % (self.__version, self.format, self.cls, self.name)

    @staticmethod
    def _splitLine(line):
        """Split lines which ends with { to two lines."""
        return line[4:-1] + "\n" + \
            (len(line) - len(line.strip()) - 4) * ' ' + '{'

    def body(self):
        """Return body string."""
        # remove None values
        _values = OrderedDict()
        for key, value in self.values.iteritems():
            if value:
                _values[key] = value

        # make python dictionary look like c++ dictionary!!
        of = json.dumps(_values, indent=4, separators=(";", "\t\t")) \
            .replace('\\"', '@').replace('"\n', ";\n").replace('"', '') \
            .replace('};', '}').replace('\t\t{', '{').replace('@', '"')

        # remove first and last {} and prettify[!] the file
        l = (line[4:] if not line.endswith('{') else self._splitLine(line)
             for line in of.split("\n")[1:-1])

        return "\n\n".join(l)

    @staticmethod
    def convertBoolValue(v=True):
        """Convert Boolean values to on/off string."""
        _v = ('off', 'on')

        if v in _v:
            return v

        if v:
            return 'on'
        else:
            return 'off'

    def toOpenFOAM(self):
        """Return OpenFOAM string."""
        return "\n".join((self.header(), self.body()))

    def save(self, projectFolder, subFolder=None):
        """Save to file.

        Args:
            projectFolder: Path to project folder as a string.
            subFolder: Optional input for subFolder (default: self.location).
        """
        subFolder = self.location.replace('"', '') if not subFolder else subFolder

        with open(os.path.join(projectFolder,
                               subFolder, self.name), "wb") as outf:
            outf.write(self.toOpenFOAM())

    def __eq__(self, other):
        """Check equality."""
        return self.values == other.values

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return self.toOpenFOAM()


class ZeroFolderFoamFile(FoamFile):
    """FoamFiles under 0 folder.

    The main difference between ZeroFolderFoamFile and FoamFile is that
    ZeroFolderFoamFile has a method to set boundary fields based on input
    geometry (e.g. Butterfly objects).
    """

    @classmethod
    def fromBFGeometries(cls, BFGeometries, values=None):
        """Init class by BFGeometries."""
        _cls = cls(values)
        _cls.setBoundaryField(BFGeometries)
        return _cls

    def setBoundaryField(self, BFGeometries):
        """Get data for getBoundaryField as a dictionary.

        Args:
            BFGeometries: List of Butterfly geometries.
        """
        self.values['boundaryField'] = getBoundaryField(
            BFGeometries, self.__class__.__name__.lower()
        )


class Condition(FoamFile):
    """OpenFOAM conditions object.

    Use this class to create conditions such as initialConditions and ABLConditions.
    Conditions don't have OpenFOAM header. It's only values.
    """

    def header(self):
        """Return conditions header."""
        return Header.header()
