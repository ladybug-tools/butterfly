#Foam File Class
from version import Version, Header
from helper import getBoundaryField
import os
import json

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
    __locations = ("0", "system", "constant")

    def __init__(self, name, cls, location=None, fileFormat="ascii",
                 defaultValues=None, values=None):
        """Init foam file."""
        self.__version = str(Version().OFVer)
        self.format  = str(fileFormat) # ascii / binary
        self.cls  = str(cls) # dictionary or field
        self.name = str(name)
        self.location = location #location is optional

        if self.location:
            if self.location in self.__locations:
                self.location = '"' + self.location + '"'
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
        self.__values = defaultValues
        self.updateValues(values)

    @property
    def values(self):
        """Return values as a dictionary."""
        return self.__values

    def updateValues(self, v):
        """Update current values from dictionat v.

        if key is not available in current values it will be added, if the key
        already exists it will be updated.
        """
        self.__values.update(v)

    @property
    def parameters(self):
        return self.values.keys()

    def getValueByParameter(self, parameter):
        try:
            return self.values[parameter]
        except KeyError:
            raise KeyError('{} is not available in {}.'.format(
                parameter, self.__class__.__name__
            ))

    def setValueByParameter(self, parameter, value):
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
        # convert python dictionary to c++ dictionary
        of = json.dumps(self.values, indent=4, separators=(";", "\t\t")) \
            .replace('"\n', ";\n").replace('"', '').replace('};', '}') \
            .replace('\t\t{', '{')

        # remove first and last {} and prettify[!] the file
        l = (line[4:] if not line.endswith('{') else self._splitLine(line)
             for line in of.split("\n")[1:-1])

        return "\n\n".join(l)

    def toOpenFoam(self):
        return "\n".join((self.header(), self.body()))

    def save(self, projectFolder, subFolder=None):
        subFolder = self.location.replace('"', '') if not subFolder else subFolder
        with open(os.path.join(projectFolder, subFolder, self.name), "wb") as outf:
            outf.write(self.toOpenFoam())

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        return self.toOpenFoam()


class ZeroFolderFoamFile(FoamFile):
    """FoamFiles under 0 folder.

    The main difference between ZeroFolderFoamFile and FoamFile is that
    ZeroFolderFoamFile has a method to set boundary fields based on input
    geometry (e.g. Butterfly objects)
    """
    def setBoundaryField(self, BFSurfaces):
        """Get data for getBoundaryField as a dictionary.

        Args:
            BFSurfaces: List of Butterfly surfaces.
        """
        self.values['boundaryField'] = getBoundaryField(
            BFSurfaces, self.__class__.__name__.lower()
        )

class Condition(FoamFile):
    """OpenFOAM conditions object.

    Use this class to create conditions such as initialConditions and ABLConditions.
    Conditions don't have OpenFOAM header. It's only values.
    """

    def header(self):
        """Return conditions header."""
        return Header.header()
