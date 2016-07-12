# All Grasshopper functions and classes should be in this file
import os
try:
    import Rhino as rc
    from scriptcontext import doc
except ImportError:
    pass

from .block import Block
from .bfsurface import BFSurface
from .core import Case

from ..windtunnel import TunnelParameters, WindTunnel
from ..boundarycondition import BoundaryCondition, \
    WindTunnelGroundBoundaryCondition, \
    WindTunnelInletBoundaryCondition, WindTunnelOutletBoundaryCondition, \
    WindTunnelTopAndSidesBoundaryCondition, WindTunnelWallBoundaryCondition
from ..z0 import Z0
from ..conditions import ABLConditions

from math import pi as PI
from collections import namedtuple


class GHWindTunnel(WindTunnel):
    """A grasshopper wind tunnel.

    Args:
        BFSurfaces: List of butterfly surfaces that will be inside the tunnel.
        windSpeed: Wind speed in m/s.
        windDirection: Wind direction as Vector3D.
        tunnelParameters: Butterfly tunnel parameters.
        landscape: An integer between 0-7 to calculate z0 (roughness).
            0: '0.0002'  # sea
            1: '0.005'   # smooth
            2: '0.03'    # open
            3: '0.10'    # roughlyOpen
            4: '0.25'    # rough
            5: '0.5'     # veryRough
            6: '1.0'     # closed
            7: '2.0'     # chaotic
        globalRefLevel: A tuple of (min, max) values for global refinment.
    """

    def __init__(self, name, BFSurfaces, windSpeed, windDirection=None,
                 tunnelParameters=None, landscape=1, globalRefLevel=None):
        """Init grasshopper wind tunnel."""
        self.name = name

        # update boundary condition of wall surfaces
        for bfSurface in BFSurfaces:
            bfSurface.boundaryCondition = WindTunnelWallBoundaryCondition(
                bfSurface.boundaryCondition.refLevels
                )

        self.BFSurfaces = BFSurfaces

        try:
            self.z0 = Z0()[landscape]
        except Exception as e:
            raise ValueError('Invalid input for landscape.\n{}'.format(landscape))

        self.windSpeed = float(windSpeed)

        self.windDirection = rc.Geometry.Vector3d.YAxis if not windDirection \
            else rc.Geometry.Vector3d(windDirection)
        self.windDirection.Unitize()

        self.tunnelParameters = TunnelParameters() if not tunnelParameters \
            else tunnelParameters

        self.plane = self.__calculatePlane()

        self.minmax, self.dimensions, self.boundingbox = self.getBoundingBox()
        self.__scaleBoundingBox()

        # create block
        block = self.block

        # create butterfly surfaces
        inlet, outlet, rightSide, leftSide, top, ground = self.boundingSurfaces

        # init openFOAM windTunnel
        super(GHWindTunnel, self).__init__(
            self.name, inlet, outlet, (rightSide, leftSide), top, ground,
            self.BFSurfaces, block, self.z0, globalRefLevel
        )

    @property
    def ghBoundingSurfaces(self):
        """Return Grasshopper surfaces of wind tunnel in a named tuple."""
        wtSrfs = namedtuple('WindTunnelSurfaces',
                          'rightSide outlet leftSide inlet ground top')

        _srfs = self.boundingbox.Surfaces

        wtSrfs.rightSide, wtSrfs.leftSide = _srfs[0], _srfs[2]
        wtSrfs.inlet, wtSrfs.outlet = _srfs[3], _srfs[1]
        wtSrfs.ground, wtSrfs.top = _srfs[4], _srfs[5]

        return wtSrfs

    @property
    def block(self):
        """Create block for this windTunnel."""
        # create block
        return Block(self.boundingbox, self.tunnelParameters.nDivXYZ, \
                     self.tunnelParameters.gradXYZ)

    @property
    def boundingSurfaces(self):
        """Return bounding surfaces of wind tunnel.

        (inlet, outlet, rightSide, leftSide, top, ground)
        """
        # creat ABLCondition
        ablConditions = ABLConditions.fromWindTunnel(self)

        # create BF surfaces for each wind tunnel surface
        inlet = BFSurface('inlet', (self.ghBoundingSurfaces.inlet.ToBrep(),),
                          WindTunnelInletBoundaryCondition(ablConditions))

        outlet = BFSurface('outlet', (self.ghBoundingSurfaces.outlet.ToBrep(),),
                           WindTunnelOutletBoundaryCondition())

        rightSide = BFSurface('rightSide',
                              (self.ghBoundingSurfaces.rightSide.ToBrep(),),
                              WindTunnelTopAndSidesBoundaryCondition())

        leftSide = BFSurface('lefttSide',
                             (self.ghBoundingSurfaces.leftSide.ToBrep(),),
                             WindTunnelTopAndSidesBoundaryCondition())

        top = BFSurface('top', (self.ghBoundingSurfaces.top.ToBrep(),),
                        WindTunnelTopAndSidesBoundaryCondition())

        ground = BFSurface('ground', (self.ghBoundingSurfaces.ground.ToBrep(),),
                           WindTunnelGroundBoundaryCondition(ablConditions))

        # return the new windTunnel
        return inlet, outlet, rightSide, leftSide, top, ground

    @property
    def ABLConditionsDict(self):
        """Get ABLCondition for this wind tunnel as a dictionary."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(self.windSpeed)
        _ABLCDict['z0'] = 'uniform {}'.format(self.z0)
        _ABLCDict['flowDir'] = '({} {} {})'.format(self.windDirection.X,
                                                   self.windDirection.Y,
                                                   self.windDirection.Z)
        _ABLCDict['zGround'] = 'uniform {}'.format(self.block.minZ)

        return _ABLCDict

    def toOpenFOAMCase(self):
        """Return a BF case for this wind tunnel."""
        return Case.fromWindTunnel(self)

    def __calculatePlane(self):
        """Calculate base plane based on wind direction."""
        # set XAxis to wind direction
        xAxis = rc.Geometry.Vector3d(self.windDirection.X,
                                     self.windDirection.Y,
                                     self.windDirection.Z)
        # calculate YAxis
        yAxis = rc.Geometry.Vector3d(xAxis)
        yAxis.Rotate(PI/2, rc.Geometry.Vector3d.ZAxis)
        return rc.Geometry.Plane(rc.Geometry.Point3d.Origin, xAxis, yAxis)

    def __getDimension(self, min, max, axis):
        """Calculate dimensions of each axis of a boundingbox."""
        perpPlane = rc.Geometry.Plane(self.plane)
        perpPlane.Rotate(PI/2, axis)

        maxN = perpPlane.ClosestPoint(max)
        maxN.Z = 0
        minN = perpPlane.ClosestPoint(min)
        minN.Z = 0

        return minN.DistanceTo(maxN)

    def getBoundingBox(self):
        """Find boundingbox for a list of geometries.

        Returns:
            minmax: min and max points of boundingbox as (min, max)
            dimensions: Dimensions of boundingbox as (xDimension, yDimension,
                zDimension)
            boundingBox: Boundingbox geometry as Brep
        """
        geometries = tuple(bfsrf.geometry for bfsrf in self.BFSurfaces)

        world = rc.Geometry.Plane.WorldXY

        plane_to_world = rc.Geometry.Transform.ChangeBasis(self.plane, world)

        uBBox = geometries[0].GetBoundingBox(self.plane)

        if len(geometries) > 1:
            for geo in geometries[1:]:
                bbox = geo.GetBoundingBox(self.plane)
                uBBox.Union(bbox)

        box = uBBox.ToBrep()
        box.Transform(plane_to_world)

        min = uBBox.Min
        min.Transform(plane_to_world)

        max = uBBox.Max
        max.Transform(plane_to_world)

        xDimension = self.__getDimension(min, max, self.plane.XAxis)
        yDimension = self.__getDimension(min, max, self.plane.YAxis)
        zDimension = max.Z - min.Z

        return (min, max), (xDimension, yDimension, zDimension), box

    def __scaleBoundingBox(self):
        """Scale original bounding box to create wind tunnel."""

        vp = rc.Geometry.VolumeMassProperties.Compute(self.boundingbox)

        cenPt = (vp.Centroid.X, vp.Centroid.Y, 0)
        vp.Dispose()

        self.plane.Origin = rc.Geometry.Point3d(*cenPt)

        xScale = (self.tunnelParameters.windward + self.tunnelParameters.leeward) \
                 * (self.dimensions[2] / self.dimensions[0]) + 1

        yScale = (2 * self.tunnelParameters.side
                  * (self.dimensions[2] / self.dimensions[1])) + 1

        zScale = self.tunnelParameters.top + 1

        _scale = rc.Geometry.Transform.Scale(self.plane, xScale, yScale, zScale)

        self.boundingbox.Transform(_scale)

        moveVector = ((self.tunnelParameters.leeward + self.tunnelParameters.windward)
                      / 2 - self.tunnelParameters.windward) \
                      * self.plane.XAxis \
                      * self.dimensions[2]

        self.boundingbox.Transform(rc.Geometry.Transform.Translation(moveVector.X,
                                                                     moveVector.Y,
                                                                     moveVector.Z))
