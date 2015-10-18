#Foam File Class
from version import Version

class FoamFile:
    """FoamFile setting

        Read (http://cfd.direct/openfoam/user-guide/basic-file-format/) for
        more information about FoamFile

        Attributes:
            name            :   Filename (e.g. controlDict)
            OFClass         :   OpenFOAM class constructed from the data file
                            concerned. Typically  dictionary  or a field, e.g. volVectorField
            location        :   Path to the file (0, constant or system)
            fileFormat  :   File format (ascii / binary) (default: ascii)

        Usage:

        """

    def __init__(self, name, OFClass, location = None, fileFormat = "ascii"):
        self.version = str(Version.OFVer())
        self.format  = str(fileFormat) # ascii / binary
        self.OFClass  = str(OFClass) #dictionary or field
        self.object = str(name)
        self.location = str(location) #location is optional
        if self.location == "0":
            self.location = '"' + self.location + '"'

    def get_OFString(self):
        """Return open foam style string"""
        if self.location:
            return "FoamFile\n{\n" + \
            "\tversion\t\t%s;\n"%self.version + \
            "\tformat\t\t%s;\n"%self.format + \
            "\tclass\t\t%s;\n"%self.OFClass + \
            "\tlocation\t\t%s;\n"%self.location + \
            "\tobject\t\t%s;\n"%self.object + \
            "}\n"
        else:
            return "FoamFile\n{\n" + \
            "\tversion\t\t%s;\n"%self.version + \
            "\tformat\t\t%s;\n"%self.format + \
            "\tclass\t\t%s;\n"%self.OFClass + \
            "\tobject\t\t%s;\n"%self.object + \
            "}\n"

ff = FoamFile("k", "volScalarField", "0")
print ff.get_OFString()
