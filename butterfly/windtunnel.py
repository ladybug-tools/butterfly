# coding=utf-8
"""Butterfly wind tunnel."""
from copy import deepcopy

from .blockMeshDict import BlockMeshDict
from .case import Case
from .meshingparameters import MeshingParameters
from .geometry import calculateMinMaxFromBFGeometries, BFBlockGeometry
from .boundarycondition import WindTunnelGroundBoundaryCondition, \
    WindTunnelInletBoundaryCondition, WindTunnelOutletBoundaryCondition, \
    WindTunnelTopAndSidesBoundaryCondition, WindTunnelWallBoundaryCondition
from .conditions import ABLConditions
import vectormath as vm


class WindTunnel(object):
    """Butterfly WindTunnel.

    Args:
        inlet: Inlet as a butterfly geometry. inlet boundary condition should be
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
        self.z0 = roughness if roughness > 0 else 0.0001

        self.__blockMeshDict = BlockMeshDict.fromBFBlockGeometries(
            self.boundingGeometries, convertToMeters)

        self.meshingParameters = meshingParameters or MeshingParameters()

        self.Zref = float(Zref) if Zref else 10
        self.convertToMeters = convertToMeters

        # place holder for refinment regions
        self.__refinementRegions = []

    @classmethod
    def fromGeometriesWindVectorAndParameters(
            cls, name, geometries, windVector, tunnelParameters, roughness,
            meshingParameters=None, Zref=None, convertToMeters=1):
        """Create a windTunnel based on size, wind speed and wind direction."""
        # butterfly geometries
        geos = tuple(cls.__checkInputGeometry(geo) for geo in geometries)

        # update boundary condition of wall geometries
        for bfGeometry in geometries:
            bfGeometry.boundaryCondition = WindTunnelWallBoundaryCondition()

        tp = tunnelParameters

        # find xAxis
        # project wind vector to XY Plane
        windVector = (windVector[0], windVector[1], 0)
        zAxis = (0, 0, 1)
        xAxis = vm.crossProduct(windVector, zAxis)
        yAxis = vm.normalize(windVector)

        # get size of bounding box from blockMeshDict
        minPt, maxPt = calculateMinMaxFromBFGeometries(geos, xAxis)
        _blockMeshDict = BlockMeshDict.fromMinMax(minPt, maxPt, convertToMeters,
                                                  xAxis=xAxis)
        # scale based on wind tunnel parameters
        ver = _blockMeshDict.vertices
        height = _blockMeshDict.height
        v0 = vm.move(ver[0], vm.scale(yAxis, -tp.windward * height))
        v0 = vm.move(v0, vm.scale(xAxis, -tp.side * height))
        v1 = vm.move(ver[1], vm.scale(yAxis, -tp.windward * height))
        v1 = vm.move(v1, vm.scale(xAxis, tp.side * height))
        v2 = vm.move(ver[2], vm.scale(yAxis, tp.leeward * height))
        v2 = vm.move(v2, vm.scale(xAxis, tp.side * height))
        v3 = vm.move(ver[3], vm.scale(yAxis, tp.leeward * height))
        v3 = vm.move(v3, vm.scale(xAxis, -tp.side * height))
        v4 = vm.move(v0, vm.scale(zAxis, tp.top * height))
        v5 = vm.move(v1, vm.scale(zAxis, tp.top * height))
        v6 = vm.move(v2, vm.scale(zAxis, tp.top * height))
        v7 = vm.move(v3, vm.scale(zAxis, tp.top * height))

        # create inlet, outlet, etc
        ablConditions = ABLConditions.fromInputValues(
            flowSpeed=vm.length(windVector), z0=roughness,
            flowDir=vm.normalize(windVector), zGround=_blockMeshDict.minZ)

        _order = (range(4),)
        inlet = BFBlockGeometry(
            'inlet', (v0, v1, v5, v4), _order, ((v0, v1, v5, v4),),
            WindTunnelInletBoundaryCondition(ablConditions))

        outlet = BFBlockGeometry(
            'outlet', (v2, v3, v7, v6), _order, ((v2, v3, v7, v6),),
            WindTunnelOutletBoundaryCondition())

        rightSide = BFBlockGeometry(
            'rightSide', (v1, v2, v6, v5), _order, ((v1, v2, v6, v5),),
            WindTunnelTopAndSidesBoundaryCondition())

        leftSide = BFBlockGeometry(
            'leftSide', (v3, v0, v4, v7), _order, ((v3, v0, v4, v7),),
            WindTunnelTopAndSidesBoundaryCondition())

        top = BFBlockGeometry('top', (v4, v5, v6, v7), _order,
                              ((v4, v5, v6, v7),),
                              WindTunnelTopAndSidesBoundaryCondition())

        ground = BFBlockGeometry(
            'ground', (v3, v2, v1, v0), (range(4),), ((v3, v2, v1, v0),),
            WindTunnelGroundBoundaryCondition(ablConditions))

        # return the class
        wt = cls(name, inlet, outlet, (rightSide, leftSide), top, ground,
                 geometries, roughness, meshingParameters, Zref,
                 convertToMeters)

        return wt

    @property
    def width(self):
        """Get width in x direction."""
        return self.blockMeshDict.width

    @property
    def height(self):
        """Get width in x direction."""
        return self.blockMeshDict.height

    @property
    def length(self):
        """Get width in x direction."""
        return self.blockMeshDict.length

    @property
    def boundingGeometries(self):
        """Return bounding geometries of wind tunnel."""
        return (self.inlet, self.outlet) + self.sides + \
               (self.top, self.ground)

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
        return self.__blockMeshDict

    @property
    def ABLConditionsDict(self):
        """Get ABLCondition for this wind tunnel as a dictionary."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(self.flowSpeed)
        _ABLCDict['z0'] = 'uniform {}'.format(self.z0)
        _ABLCDict['flowDir'] = self.flowDir if isinstance(self.flowDir, str) \
            else '({} {} {})'.format(*self.flowDir)
        _ABLCDict['zGround'] = 'uniform {}'.format(self.zGround)
        return _ABLCDict

    @property
    def meshingParameters(self):
        """Meshing parameters."""
        return self.__meshingParameters

    @meshingParameters.setter
    def meshingParameters(self, mp):
        """Update meshing parameters."""
        if not mp:
            return
        assert hasattr(mp, 'isMeshingParameters'), \
            'Excepted Meshingparameters not {}'.format(type(mp))
        self.__meshingParameters = mp
        self.blockMeshDict.updateMeshingParameters(mp)

    def addRefinementRegion(self, refinementRegion):
        """Add refinement regions to this case."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)

    @staticmethod
    def __checkInputGeometry(input):
        if hasattr(input, 'isBFGeometry'):
            return input
        else:
            raise ValueError('{} is not a Butterfly geometry.'.format(input))

    def toOpenFOAMCase(self, make2dParameters=None):
        """Return a BF case for this wind tunnel."""
        return Case.fromWindTunnel(self, make2dParameters)

    def save(self, overwrite=False, minimum=True, make2dParameters=None):
        """Save windTunnel to folder as an OpenFOAM case.

        Args:
            overwrite: If True all the current content will be overwritten
                (default: False).
        Returns:
            A butterfly.Case.
        """
        _case = self.toOpenFOAMCase(make2dParameters)
        _case.save(overwrite, minimum)
        return _case

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Wind tunnel."""
        return "WindTunnel::%.2f * %.2f * %.2f::dir %s::%.3f m/s" % (
            self.width, self.length, self.height, self.flowDir,
            float(self.flowSpeed))


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

    @staticmethod
    def __checkInput(input):
        """Check input values."""
        try:
            _inp = float(input)
        except TypeError:
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
