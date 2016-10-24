# coding=utf-8
"""Butterfly wind tunnel."""
from copy import deepcopy

from .blockMeshDict import BlockMeshDict
from .case import Case
from .grading import SimpleGrading
from meshingparameters import MeshingParameters


class WindTunnel(object):
    """Butterfly WindTunnel.

    Args:
        inlet: Inlet as a honeybee geometry. inlet boundary condition should be
            ABL (atmBoundaryLayer).
        outlet: Outlet as a butterfly geometry.
        sides: Left and right side geometries as butterfly geometries.
        top: Top face as buttefly geometry.
        ground: Ground face as butterfly geometry.
        testGeomtries: A list of geometries as butterfly geometries that are located
            within bounding box boundary.
        roughness: z0 (roughness) value.
                '0.0002'  # sea
                '0.005'   # smooth
                '0.03'    # open
                '0.10'    # roughlyOpen
                '0.25'    # rough
                '0.5'     # veryRough
                '1.0'     # closed
                '2.0'     # chaotic
        Zref: Reference height for wind velocity in meters (default: 10).
    """

    def __init__(self, name, inlet, outlet, sides, top, ground, testGeomtries,
                 roughness, meshingParameters=None, Zref=None, convertToMeters=1):
        """Init wind tunnel."""
        self.name = str(name)
        self.inlet = self.__checkInputGeometry(inlet)
        self.outlet = self.__checkInputGeometry(outlet)
        self.sides = tuple(side for side in sides if self.__checkInputGeometry(side))
        self.top = self.__checkInputGeometry(top)
        self.ground = self.__checkInputGeometry(ground)
        self.testGeomtries = tuple(geo for geo in testGeomtries
                                   if self.__checkInputGeometry(geo))
        self.z0 = roughness
        self.meshingParameters = meshingParameters or MeshingParameters()

        self.Zref = float(Zref) or 10
        self.convertToMeters = convertToMeters

        # place holder for refinment regions
        self.__refinementRegions = []

    @property
    def boundingGeometries(self):
        """Return bounding geometries of wind tunnel."""
        return (self.inlet, self.outlet) + self.sides + \
               (self.top, self.ground)

    def __checkInputGeometry(self, input):
        if hasattr(input, 'isBFGeometry'):
            return input
        else:
            raise ValueError('{} is not a Butterfly geometry.'.format(input))

    @property
    def refinementRegions(self):
        """Get refinement regions."""
        return self.__refinementRegions

    @property
    def flowDir(self):
        """Get flow direction for this wind tunnel as a tuple (x, y, z)."""
        return self.inlet.boundaryCondition.U.flowDir

    @property
    def flowSpeed(self):
        """Get flow speed for this wind tunnel."""
        return self.inlet.boundaryCondition.U.Uref

    @property
    def zGround(self):
        """Minimum z value of the bounding box."""
        return self.blockMeshDict.minZ

    @property
    def blockMeshDict(self):
        """Wind tunnel blockMeshDict."""
        bmdict = BlockMeshDict.fromBFBlockGeometries(
                self.boundingGeometries, self.convertToMeters)
        bmdict.updateMeshingParameters(self.meshingParameters)
        return bmdict

    @property
    def ABLConditionsDict(self):
        """Get ABLCondition for this wind tunnel as a dictionary."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(self.flowSpeed)
        _ABLCDict['z0'] = 'uniform {}'.format(self.z0)
        _ABLCDict['flowDir'] = '({} {} {})'.format(*self.flowDir)
        _ABLCDict['zGround'] = 'uniform {}'.format(self.zGround)
        return _ABLCDict

    def addRefinementRegion(self, refinementRegion):
        """Add refinement regions to this case."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)

    def toOpenFOAMCase(self):
        """Return a BF case for this wind tunnel."""
        return Case.fromWindTunnel(self)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Wind tunnel."""
        return "WindTunnel :: dir {} :: {} m/s".format(self.flowDir,
                                                       self.flowSpeed)


class TunnelParameters(object):
    """Wind tunnel parameters.

    Each parameter will be multiplied by multiple height.

    Args:
        windward: Multiplier value for windward extension (default: 3).
        top: Multiplier value for top extension (default: 3).
        side: Multiplier value for side extension (default: 2).
        leeward: Multiplier value for leeward extension (default: 15).
    """

    def __init__(self, windward=3, top=3, side=2, leeward=15):
        """Init wind tunnel parameters."""
        self.windward = self.__checkInput(windward)
        self.top = self.__checkInput(top)
        self.side = self.__checkInput(side)
        self.leeward = self.__checkInput(leeward)

    def __checkInput(self, input):
        """Check input values."""
        try:
            _inp = float(input)
        except:
            raise ValueError("Failed to convert %s to a number." % input)
        else:
            assert _inp > 0, "Value (%.2f) should be larger than 0." % _inp
            return _inp

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return 'WW: %.1fX; T: %.1fX; S: %.1fX; LW: %.1fX;' % (
            self.windward, self.top, self.side, self.leeward)
