# coding=utf-8
"""Butterfly wind tunnel."""
from copy import deepcopy

from .blockMeshDict import BlockMeshDict
from .case import Case
from .meshingparameters import MeshingParameters
from .geometry import calculate_min_max_from_bf_geometries, BFBlockGeometry
from .boundarycondition import WindTunnelGroundBoundaryCondition, \
    WindTunnelInletBoundaryCondition, WindTunnelOutletBoundaryCondition, \
    WindTunnelTopAndSidesBoundaryCondition, WindTunnelWallBoundaryCondition
from .conditions import ABLConditions

import vectormath as vm
import grading
import gradingutil as gutil


class WindTunnel(object):
    """Butterfly WindTunnel.

    Args:
        inlet: Inlet as a butterfly geometry. inlet boundary condition should be
            ABL (atmBoundaryLayer).
        outlet: Outlet as a butterfly geometry.
        sides: Left and right side geometries as butterfly geometries.
        top: Top face as buttefly geometry.
        ground: Ground face as butterfly geometry.
        test_geomtries: A list of geometries as butterfly geometries that are located
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

    def __init__(self, name, inlet, outlet, sides, top, ground, test_geomtries,
                 roughness, meshing_parameters=None, Zref=None, convertToMeters=1):
        """Init wind tunnel."""
        self.name = str(name)
        self.inlet = self._check_input_geometry(inlet)
        self.outlet = self._check_input_geometry(outlet)
        self.sides = tuple(side for side in sides if self._check_input_geometry(side))
        self.top = self._check_input_geometry(top)
        self.ground = self._check_input_geometry(ground)
        self.test_geomtries = tuple(geo for geo in test_geomtries
                                    if self._check_input_geometry(geo))
        self.z0 = roughness if roughness > 0 else 0.25

        self.__blockMeshDict = BlockMeshDict.from_bf_block_geometries(
            self.bounding_geometries, convertToMeters)

        self.meshing_parameters = meshing_parameters or MeshingParameters()

        self.Zref = float(Zref) if Zref else 10
        self.convertToMeters = convertToMeters

        # place holder for refinment regions
        self.__refinementRegions = []

    @classmethod
    def from_geometries_wind_vector_and_parameters(
            cls, name, geometries, wind_vector, tunnel_parameters, roughness,
            meshing_parameters=None, Zref=None, convertToMeters=1):
        """Create a wind_tunnel based on size, wind speed and wind direction."""
        # butterfly geometries
        geos = tuple(cls._check_input_geometry(geo) for geo in geometries)

        # update boundary condition of wall geometries
        for bfGeometry in geometries:
            bfGeometry.boundary_condition = WindTunnelWallBoundaryCondition()

        tp = tunnel_parameters

        # find x_axis
        # project wind vector to XY Plane
        wind_vector = (wind_vector[0], wind_vector[1], 0)
        z_axis = (0, 0, 1)
        x_axis = vm.cross_product(wind_vector, z_axis)
        y_axis = vm.normalize(wind_vector)

        # get size of bounding box from blockMeshDict
        min_pt, max_pt = calculate_min_max_from_bf_geometries(geos, x_axis)
        _blockMeshDict = BlockMeshDict.from_min_max(min_pt, max_pt, convertToMeters,
                                                    x_axis=x_axis)
        # scale based on wind tunnel parameters
        ver = _blockMeshDict.vertices
        height = _blockMeshDict.height
        v0 = vm.move(ver[0], vm.scale(y_axis, -tp.windward * height))
        v0 = vm.move(v0, vm.scale(x_axis, -tp.side * height))
        v1 = vm.move(ver[1], vm.scale(y_axis, -tp.windward * height))
        v1 = vm.move(v1, vm.scale(x_axis, tp.side * height))
        v2 = vm.move(ver[2], vm.scale(y_axis, tp.leeward * height))
        v2 = vm.move(v2, vm.scale(x_axis, tp.side * height))
        v3 = vm.move(ver[3], vm.scale(y_axis, tp.leeward * height))
        v3 = vm.move(v3, vm.scale(x_axis, -tp.side * height))
        v4 = vm.move(v0, vm.scale(z_axis, tp.top * height))
        v5 = vm.move(v1, vm.scale(z_axis, tp.top * height))
        v6 = vm.move(v2, vm.scale(z_axis, tp.top * height))
        v7 = vm.move(v3, vm.scale(z_axis, tp.top * height))

        # create inlet, outlet, etc
        abl_conditions = ABLConditions.from_input_values(
            flow_speed=vm.length(wind_vector), z0=roughness,
            flowDir=vm.normalize(wind_vector), zGround=_blockMeshDict.min_z)

        _order = (range(4),)
        inlet = BFBlockGeometry(
            'inlet', (v0, v1, v5, v4), _order, ((v0, v1, v5, v4),),
            WindTunnelInletBoundaryCondition(abl_conditions))

        outlet = BFBlockGeometry(
            'outlet', (v2, v3, v7, v6), _order, ((v2, v3, v7, v6),),
            WindTunnelOutletBoundaryCondition())

        right_side = BFBlockGeometry(
            'right_side', (v1, v2, v6, v5), _order, ((v1, v2, v6, v5),),
            WindTunnelTopAndSidesBoundaryCondition())

        left_side = BFBlockGeometry(
            'left_side', (v3, v0, v4, v7), _order, ((v3, v0, v4, v7),),
            WindTunnelTopAndSidesBoundaryCondition())

        top = BFBlockGeometry('top', (v4, v5, v6, v7), _order,
                              ((v4, v5, v6, v7),),
                              WindTunnelTopAndSidesBoundaryCondition())

        ground = BFBlockGeometry(
            'ground', (v3, v2, v1, v0), (range(4),), ((v3, v2, v1, v0),),
            WindTunnelGroundBoundaryCondition(abl_conditions))

        # return the class
        wt = cls(name, inlet, outlet, (right_side, left_side), top, ground,
                 geometries, roughness, meshing_parameters, Zref,
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
    def bounding_geometries(self):
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
        return self.inlet.boundary_condition.U.flowDir

    @property
    def flow_speed(self):
        """Get flow speed for this wind tunnel."""
        return self.inlet.boundary_condition.U.Uref

    @property
    def zGround(self):
        """Minimum z value of the bounding box."""
        return self.blockMeshDict.min_z

    @property
    def blockMeshDict(self):
        """Wind tunnel blockMeshDict."""
        return self.__blockMeshDict

    @property
    def ABLConditionsDict(self):
        """Get ABLCondition for this wind tunnel as a dictionary."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(self.flow_speed)
        _ABLCDict['z0'] = 'uniform {}'.format(self.z0)
        _ABLCDict['flowDir'] = self.flowDir if isinstance(self.flowDir, str) \
            else '({} {} {})'.format(*self.flowDir)
        _ABLCDict['zGround'] = 'uniform {}'.format(self.zGround)
        return _ABLCDict

    @property
    def meshing_parameters(self):
        """Meshing parameters."""
        return self.__meshing_parameters

    @meshing_parameters.setter
    def meshing_parameters(self, mp):
        """Update meshing parameters."""
        if not mp:
            return
        assert hasattr(mp, 'isMeshingParameters'), \
            'Excepted Meshingparameters not {}'.format(type(mp))
        self.__meshing_parameters = mp
        self.blockMeshDict.update_meshing_parameters(mp)

    def get_internal_dimensions(self):
        """Get internal dimensions of wind tunnel.

        This method returns three tuples for x, y and z which are
        (distance_to_geometry_bounding_box, geometry_bounding_box,
         distance_after_geometry_bounding_box). This method is useful to get initial
         values to calculate grading.
        """
        x_axis = self.blockMeshDict.x_axis
        min_pt, max_pt = calculate_min_max_from_bf_geometries(self.test_geomtries,
                                                              x_axis)
        # rotate points to xy axis
        angle = vm.angle_anitclockwise((1, 0, 0), x_axis)
        min_pt = vm.rotate((0, 0, 0), min_pt, -angle)
        max_pt = vm.rotate((0, 0, 0), max_pt, -angle)
        wt_min_pt = vm.rotate((0, 0, 0), self.blockMeshDict.min_pt, -angle)
        wt_max_pt = vm.rotate((0, 0, 0), self.blockMeshDict.max_pt, -angle)

        x_values = \
            (min_pt[0] - wt_min_pt[0], max_pt[0] - min_pt[0], wt_max_pt[0] - max_pt[0])

        y_values = \
            (min_pt[1] - wt_min_pt[1], max_pt[1] - min_pt[1], wt_max_pt[1] - max_pt[1])

        z_values = \
            (min_pt[2] - wt_min_pt[2], max_pt[2] - min_pt[2], wt_max_pt[2] - max_pt[2])

        return x_values, y_values, z_values

    def calculate_grading(self, cell_size=1, expansion_ratio=1.2, wake_offset=2,
                          height_offset=5, z_mode=0):
        """Calculate simpleGrading for this wind tunnel based on best practice.

        This method calcutes grading for blockMeshDict based on the size of the wind
        tunnel and the bounding box of the geometries.


        Args:
            cell_size: Cell size in the area of interest (default: 1).
            expansion_ratio: expansion ratio for the segments outside the area of
                interest (default: 1.2).
            wake_offset: The length to be added to the end of geometries bounding
                box to be considerd as part of area of interest (default: 2).
            height_offset: The length to be added to the topic of geometries bounding
                box to be considerd as part of area of interest (default: 5).
            z_mode: If 0 special treatment will be considerd for the first 2 and 10
                meters. The first 2 meters will be graded for each half meter and from
                2-10 it will be graded 0.5-1, from 10 to maximum height it will be 1-5
                if expansion ration is less than expansion ratio then expansion ratio
                will be used. After 10 meters normal expansion_ratio will be used.
                If 1, z direction will be treated similar to x and y (default: 0).
        Returns:
            SimpleGrading, cell_count as (x_count, y_count, z_count)

        """
        x_dim, y_dim, z_dim = self.get_internal_dimensions()
        # adjust for wake offset
        y_dim = (y_dim[0], y_dim[1] + wake_offset, y_dim[2] - wake_offset)
        z_dim = (z_dim[0], z_dim[1] + height_offset, z_dim[2] - height_offset)

        # calculate cell counts and grading for each direction
        # x direction
        # before the area of interest
        x_0_grd_data = gutil.grading_by_length_de_ccratio(
            x_dim[0], cell_size, 1.0 / expansion_ratio, 0.01)
        x_0_grd = grading.Grading(x_dim[0], x_0_grd_data.n, x_0_grd_data.r)
        # area of interest
        x_1_grd = grading.Grading(x_dim[1], int(x_dim[1] / cell_size), 1)
        # after the area of interest
        x_2_grd_data = gutil.grading_by_length_ds_ccratio(
            x_dim[2], cell_size, expansion_ratio)
        x_2_grd = grading.Grading(x_dim[2], x_2_grd_data.n, x_2_grd_data.r)
        x_cell_count = x_0_grd_data.n + int(x_dim[1] / cell_size) + x_2_grd_data.n
        x_grd = grading.MultiGrading((x_0_grd, x_1_grd, x_2_grd))
        print('x_0: {}'.format(x_0_grd_data))
        print('x_2: {}'.format(x_2_grd_data))

        # y direction
        # before the area of interest
        y_0_grd_data = gutil.grading_by_length_de_ccratio(
            y_dim[0], cell_size, 1.0 / expansion_ratio, 0.01)
        y_0_grd = grading.Grading(y_dim[0], y_0_grd_data.n, y_0_grd_data.r)
        # area of interest
        y_1_grd = grading.Grading(y_dim[1], int(y_dim[1] / cell_size), 1)
        # after the area of interest
        y_2_grd_data = gutil.grading_by_length_ds_ccratio(
            y_dim[2], cell_size, expansion_ratio)
        y_2_grd = grading.Grading(y_dim[2], y_2_grd_data.n, y_2_grd_data.r)
        y_cell_count = y_0_grd_data.n + int(y_dim[1] / cell_size) + y_2_grd_data.n
        y_grd = grading.MultiGrading((y_0_grd, y_1_grd, y_2_grd))
        print('y_0: {}'.format(y_0_grd_data))
        print('y_2: {}'.format(y_2_grd_data))

        # z direction
        # before the area of interest
        z_grd_col = []
        z_cell_count = 0
        if z_mode == 0:
            z_0_grd = grading.Grading(2, 4, 1)  # 4 * 0.5 for the first 2 meters
            z_grd_col.append(z_0_grd)
            z_cell_count += 4
            z_1_grd = grading.Grading(8, 11, 1.07)  # go from 0.5-1 up to 10 meters
            z_grd_col.append(z_1_grd)
            z_cell_count += 11

            geometry_z = z_dim[0] + z_dim[1]
            if geometry_z - 10 > 5 * expansion_ratio:
                distance = geometry_z - 10
                z_3_grd_data = gutil.grading_by_length_ds_de(
                    distance, 1 * expansion_ratio, 5)
                z_3_grd = grading.Grading(distance, z_3_grd_data.n, z_3_grd_data.r)
                z_grd_col.append(z_3_grd)
                z_cell_count += z_3_grd_data.n

            # final part of the wind tunnel
            z_4_grd_data = gutil.grading_by_length_ds_ccratio(
                z_dim[2], cell_size, expansion_ratio)
            z_4_grd = grading.Grading(z_dim[2], z_4_grd_data.n, z_4_grd_data.r)
            z_cell_count += z_4_grd_data.n
            z_grd_col.append(z_4_grd)
        else:
            if not z_dim[0] == 0:
                z_0_grd_data = gutil.grading_by_length_de_ccratio(
                    z_dim[0], cell_size, 1.0 / expansion_ratio, 0.01
                )
                z_0_grd = grading.Grading(z_dim[0], z_0_grd_data.n, z_0_grd_data.r)
                z_grd_col.append(z_0_grd)
                z_cell_count += z_0_grd_data.n
            # area of interest
            z_1_grd = grading.Grading(z_dim[1], int(y_dim[1] / cell_size), 1)
            z_grd_col.append(z_1_grd)
            z_cell_count += int(y_dim[0] / cell_size)

            # after the area of interest
            z_2_grd_data = gutil.grading_by_length_ds_ccratio(
                y_dim[2], cell_size, expansion_ratio)
            z_2_grd = grading.Grading(z_dim[2], z_2_grd_data.n, z_2_grd_data.r)
            z_grd_col.append(z_2_grd)
            z_cell_count += z_2_grd_data.n

        z_grd = grading.MultiGrading(z_grd_col)
        grd = grading.SimpleGrading(x_grd, y_grd, z_grd)
        return grd, (x_cell_count, y_cell_count, z_cell_count)

    def add_refinementRegion(self, refinementRegion):
        """Add refinement regions to this case."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)

    @staticmethod
    def _check_input_geometry(input):
        if hasattr(input, 'isBFGeometry'):
            return input
        else:
            raise ValueError('{} is not a Butterfly geometry.'.format(input))

    def to_openfoam_case(self, make2d_parameters=None):
        """Return a BF case for this wind tunnel."""
        return Case.from_wind_tunnel(self, make2d_parameters)

    def save(self, overwrite=False, minimum=True, make2d_parameters=None):
        """Save wind_tunnel to folder as an OpenFOAM case.

        Args:
            overwrite: If True all the current content will be overwritten
                (default: False).
        Returns:
            A butterfly.Case.
        """
        _case = self.to_openfoam_case(make2d_parameters)
        _case.save(overwrite, minimum)
        return _case

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Wind tunnel."""
        return "WindTunnel::%.2f * %.2f * %.2f::dir %s::%.3f m/s" % (
            self.width, self.length, self.height, self.flowDir,
            float(self.flow_speed))


class TunnelParameters(object):
    """Wind tunnel parameters.

    Each parameter will be multiplied by multiple height.

    Args:
        windward: Multiplier value for windward extension (default: 3).
        top: Multiplier value for top extension (default: 5).
        side: Multiplier value for side extension (default: 5).
        leeward: Multiplier value for leeward extension (default: 15).
    """

    def __init__(self, windward=3, top=5, side=5, leeward=15):
        """Init wind tunnel parameters."""
        self.windward = self.__check_input(windward)
        self.top = self.__check_input(top)
        self.side = self.__check_input(side)
        self.leeward = self.__check_input(leeward)

    @staticmethod
    def __check_input(input):
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
