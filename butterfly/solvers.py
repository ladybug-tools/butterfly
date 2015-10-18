# OpenFoam Solvers
from foamfile import FoamFile as ff
from fields import BoundaryField as bouf
from fields import Dimensions as dimensions
from fields import InternalField as intf

class Solver:
    """alphat in 0 floder"""
    def __init__(self, fileClass = "volScalarField"):
        self.FoamFile = Util.set_foamFile("alphat", fileClass, "0")
        #self.dimensions = Util.set_dimensions()
        #self.internalField = Util.set_internalField()
        #self.boundaryField = Util.set_boundaryField()
