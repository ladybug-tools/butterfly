#Foam File Class
from version import Version, Header
import os


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

    def __init__(self, name, cls, location=None, fileFormat="ascii",
                 defaultValues=None, values=None):
        """Init foam file."""
        self.__version = str(Version.OFVer())
        self.format  = str(fileFormat) # ascii / binary
        self.cls  = str(cls) # dictionary or field
        self.name = str(name)
        self.location = location #location is optional
        if self.location == "0" or self.location == "system":
            self.location = '"' + self.location + '"'

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

    def body(self):
        """Return body string."""
        return "\n".join(tuple("{}\t\t{};\n".format(key, value)
                      for key, value in self.values.iteritems()
                      ))

    def toOpenFoam(self):
        return "\n".join((self.header(), self.body()))

    def save(self, projectFolder, subFolder=None):
        subFolder = self.location.replace('"', '') if not subFolder else subFolder
        with open(os.path.join(projectFolder, subFolder, self.name), "wb") as outf:
            outf.write(self.toOpenFoam())

    def __repr__(self):
        return self.toOpenFoam()

    def header(self):
        """Return open foam style string"""
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
