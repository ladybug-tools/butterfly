# OpenFoam Solvers
from version import Header as header
from foamfile import FoamFile as ff
from fields import BoundaryField as bouf
from fields import Dimensions as dimensions
from fields import InternalField as intf

class Solver:
    """Solver base class"""
    def __init__(self, name, OFClass, location = "0", inFieldValue = ""):
        self.name = name
        self.location = location
        self.FoamFile = ff(name, OFClass, location)
        self.dimensions = dimensions()
        self.internalField = intf(inFieldValue)
        self.boundaryFields = [] #place holder for boundary fields

    # TODO: check for duplicate names
    # Seems that bfTyps and value is always the same for all the fields
    # I will set it to a default value for specific solvers
    def add_boundaryField(self, name, bfType = None, value= None, other = {}):
        # create boundary field
        if bfType == None: bfType = self.bfType
        if value == None: value = self.bfValue
        bf = bouf(name, bfType, value, other)
        self.boundaryFields.append(bf)

    def get_OFString(self):
        fileComponents = [header.get_header(),
            self.FoamFile.get_OFString(),
            self.dimensions.get_OFString(),
            self.internalField.get_OFString(),
            bouf.get_BoundaryFieldsOFString(self.boundaryFields)]

        return "\n".join(fileComponents)

    def writeToFile(self, filepath):
        with open(filepath + self.name, "w") as outf:
            outf.write(self.get_OFString())

    def __repr__(self):
        return self.get_OFString()


class Alphat(Solver):
    """Alphat solver

        Usage:
            alphat = Alphat()
            alphat.add_boundaryField("floor")
            alphat.add_boundaryField("ceiling")
            alphat.add_boundaryField("fixedWalls")
            print alphat.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "alphat", "volScalarField",
            inFieldValue = "uniform 0")
        self.dimensions.update(0, 2, -1, 0, 0, 0, 0)
        self.bfType = "alphatJayatillekeWallFunction"
        self.bfValue = "0"


class Epsilon(Solver):
    """Epsilon solver

        Usage:
            epsilon = Epsilon()
            epsilon.add_boundaryField("floor")
            epsilon.add_boundaryField("ceiling")
            epsilon.add_boundaryField("fixedWalls")
            print epsilon.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "epsilon", "volScalarField",
            inFieldValue = "uniform 0.01")
        self.dimensions.update(0, 2, 3, 0, 0, 0, 0)
        self.bfType = "epsilonWallFunction"
        self.bfValue = "0.01"


class K(Solver):
    """K solver

        Usage:
            k = K()
            k.add_boundaryField("floor")
            k.add_boundaryField("ceiling")
            k.add_boundaryField("fixedWalls")
            print k.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "k", "volScalarField", inFieldValue = "uniform 0.01")
        self.dimensions.update(0, 2, -2, 0, 0, 0, 0)
        self.bfType = "alphatJayatillekeWallFunction"
        self.bfValue = "0.01"


class Nut(Solver):
    """Nut solver

        Usage:
            nut = Nut()
            nut.add_boundaryField("floor")
            nut.add_boundaryField("ceiling")
            nut.add_boundaryField("fixedWalls")
            print nut.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "nut", "volScalarField",
            inFieldValue = "uniform 0")
        self.dimensions.update(0, 2, -1, 0, 0, 0, 0)
        self.bfType = "nutkWallFunction"
        self.bfValue = "0.0"


class P(Solver):
    """P solver

        Usage:
            p = P()
            p.add_boundaryField("floor")
            p.add_boundaryField("ceiling")
            p.add_boundaryField("fixedWalls")
            print p.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "p", "volScalarField",
            inFieldValue = "uniform 0")
        self.dimensions.update(0, 2, -2, 0, 0, 0, 0)
        self.bfType = "calculated"
        self.bfValue = "$internalField"


class P_RGH(Solver):
    """P solver

        Usage:
            p_rgh = P_RGH()
            p_rgh.add_boundaryField("floor", other = {"rho":"rhok"})
            p_rgh.add_boundaryField("ceiling", other = {"rho":"rhok"})
            p_rgh.add_boundaryField("fixedWalls", other = {"rho":"rhok"})
            print p_rgh.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "p_rgh", "volScalarField",
            inFieldValue = "uniform 0")
        self.dimensions.update(0, 2, -2, 0, 0, 0, 0)
        self.bfType = "fixedFluxPressure"
        self.bfValue = "uniform 0"


class T(Solver):
    """T solver

        Usage:
            t = T()
            t.add_boundaryField("floor")
            t.add_boundaryField("ceiling")
            # value is differnt from default values
            t.add_boundaryField("fixedWalls", bfType =zeroGradient, value = None)
            print t.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "t", "volScalarField",
            inFieldValue = "uniform 300")
        self.dimensions.update(0, 2, -1, 0, 0, 0, 0)
        self.bfType = "fixedValue"
        self.bfValue = "uniform 300"


class U(Solver):
    """U solver

        Usage:
            u = U()
            u.add_boundaryField("floor")
            u.add_boundaryField("ceiling")
            u.add_boundaryField("fixedWalls")
            print u.get_OFString()
    """
    def __init__(self):
        Solver.__init__(self, "u", "volScalarField",
            inFieldValue = "uniform (0 0 0)")
        self.dimensions.update(0, 1, -1, 0, 0, 0, 0)
        self.bfType = "fixedValue"
        self.bfValue = "uniform (0 0 0)"
