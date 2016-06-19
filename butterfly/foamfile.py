#Foam File Class
from version import Version, Header

class FoamFile(object):
    """FoamFile base class.

    Read (http://cfd.direct/openfoam/user-guide/basic-file-format/) for
    more information about FoamFile

    Attributes:
        name: Filename (e.g. controlDict)
        OFClass: OpenFOAM class constructed from the data file
            concerned. Typically  dictionary  or a field, e.g. volVectorField
        location: Folder name (0, constant or system)
        fileFormat: File format (ascii / binary) (default: ascii)

    Usage:
        ff = FoamFile("k", "volScalarField", "0")
        print ff.header()
    """
    def __init__(self, name, cls, location=None, fileFormat="ascii"):
        self.__version = str(Version.OFVer())
        self.format  = str(fileFormat) # ascii / binary
        self.cls  = str(cls) # dictionary or field
        self.object = str(name)
        self.location = location #location is optional
        if self.location == "0":
            self.location = '"' + self.location + '"'

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
                         self.object)

        else:
            return Header.header() + \
            "FoamFile\n{\n" \
            "\tversion\t\t%s;\n" \
            "\tformat\t\t%s;\n" \
            "\tclass\t\t%s;\n" \
            "\tobject\t\t%s;\n" \
            "}\n" % (self.__version, self.format, self.cls, self.object)
