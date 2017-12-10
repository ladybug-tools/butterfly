# coding=utf-8
"""BF geometry library."""
import os
from copy import deepcopy
from .boundarycondition import IndoorWallBoundaryCondition
from .stl import read_ascii_string
from .vectormath import cross_product, rotate, angle_anitclockwise


class _BFMesh(object):
    """Base mesh geometry.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        face_indices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
    """

    def __init__(self, name, vertices, face_indices, normals=None):
        """Init Butterfly mesh."""
        self.name = name

        self.__vertices = vertices
        self.__face_indices = face_indices

        if not normals:
            normals = self.__calculate_normals()

        self.__normals = normals

        assert len(self.__face_indices) == len(self.__normals), \
            "Length of face_indices (%d) " \
            "should be equal to Length of normals (%d)" % (
                len(self.__face_indices), len(self.__normals))

        self.__calculate_min_max()

    @property
    def name(self):
        """Butterfly geometry name."""
        return self.__name

    @name.setter
    def name(self, n):
        assert n.replace('_', '').isalnum(), \
            "Name can only be alphabet, numerical values or underscore."
        self.__name = n

    @property
    def isBFMesh(self):
        """Return True for Butterfly meshes."""
        return True

    @property
    def vertices(self):
        """A flatten list of (x, y, z) for vertices."""
        return self.__vertices

    @property
    def face_indices(self):
        """A flatten list of (a, b, c) for indices for each face."""
        return self.__face_indices

    @property
    def normals(self):
        """A flatten list of (x, y, z) for normals."""
        return self.__normals

    @property
    def min(self):
        return self.__min

    @property
    def max(self):
        return self.__max

    def __calculate_normals(self):
        """Calculate normals from vertices."""
        return tuple(self.__calculate_normal_from_points(
            tuple(self.vertices[i] for i in ind)) for ind in self.face_indices)

    @staticmethod
    def __calculate_normal_from_points(pts):
        """Calculate normal for three points."""
        # vector between first point and the second point on the list
        try:
            pt1, pt2, pt3 = pts[:3]
        except Exception as e:
            raise ValueError('Failed to calculate normal:\n\t{}'.format(e))

        v1 = (pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2])

        # vector between first point and the last point in the list
        v2 = (pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2])

        return cross_product(v1, v2)

    def __calculate_min_max(self):
        """Calculate maximum and minimum x, y, z for this geometry."""
        min_pt = list(self.vertices[0])
        max_pt = list(self.vertices[0])

        for v in self.vertices[1:]:
            for i in xrange(3):
                if v[i] < min_pt[i]:
                    min_pt[i] = v[i]
                elif v[i] > max_pt[i]:
                    max_pt[i] = v[i]

        self.__min = min_pt
        self.__max = max_pt

    def to_stl(self, convertToMeters=1):
        """Get STL definition for this geometry as a string.

        Args:
            convertToMeters: A value to scale the geometry to meters. For isinstance
                if the mesh is in mm the value should be 0.001 (default: 1).
        """
        _hea = "solid {}".format(self.name)
        _tale = "endsolid {}".format(self.name)
        _body = "   facet normal {0} {1} {2}\n" \
                "     outer loop\n" \
                "       vertex {3} {4} {5}\n" \
                "       vertex {6} {7} {8}\n" \
                "       vertex {9} {10} {11}\n" \
                "     endloop\n" \
                "   endfacet"

        _bodyCollector = tuple(_body.format(
            self.__normals[count][0],
            self.__normals[count][1],
            self.__normals[count][2],
            self.__vertices[faceInd[0]][0] * convertToMeters,
            self.__vertices[faceInd[0]][1] * convertToMeters,
            self.__vertices[faceInd[0]][2] * convertToMeters,
            self.__vertices[faceInd[1]][0] * convertToMeters,
            self.__vertices[faceInd[1]][1] * convertToMeters,
            self.__vertices[faceInd[1]][2] * convertToMeters,
            self.__vertices[faceInd[2]][0] * convertToMeters,
            self.__vertices[faceInd[2]][1] * convertToMeters,
            self.__vertices[faceInd[2]][2] * convertToMeters
        ) for count, faceInd in enumerate(self.__face_indices))

        return "{}\n{}\n{}\n".format(
            _hea, "\n".join(_bodyCollector), _tale
        )

    def write_to_stl(self, folder, convertToMeters=1):
        """Save BFFace to a stl file. File name will be self.name.

        Args:
            convertToMeters: A value to scale the geometry to meters. For isinstance
                if the mesh is in mm the value should be 0.001 (default: 1).
        """
        with open(os.path.join(folder, "{}.stl".format(self.name)), "wb") as outf:
            outf.write(self.to_stl(convertToMeters))

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Butterfly mesh representation."""
        return "{}:{}".format(self.__class__.__name__, self.name)


class BFGeometry(_BFMesh):
    """Butterfly geometry.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        face_indices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
        boundary_condition: Boundary condition for this geometry.

    Usage:

        vertices = ((0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0))

        geo = BFGeometry(name='square', vertices=vertices,
                         face_indices=((0, 1, 2), (0, 2, 3)),
                         normals=((0, 0, 1), (0, 0, 1)))

        print(geo.to_stl(convertToMeters=1))
    """

    def __init__(self, name, vertices, face_indices, normals=None,
                 boundary_condition=None, refinementLevels=None,
                 nSurfaceLayers=None):
        """Init Butterfly geometry."""
        _BFMesh.__init__(self, name, vertices, face_indices, normals)
        self.boundary_condition = boundary_condition
        self.refinementLevels = refinementLevels
        self.nSurfaceLayers = nSurfaceLayers

    @property
    def isBFGeometry(self):
        """Return True for Butterfly geometries."""
        return True

    @property
    def boundary_condition(self):
        """Boundary condition."""
        return self.__bc

    @boundary_condition.setter
    def boundary_condition(self, bc):
        if not bc:
            bc = IndoorWallBoundaryCondition()

        assert hasattr(bc, 'isBoundaryCondition'), \
            '{} is not a Butterfly boundary condition.'.format(bc)

        self.__bc = bc
        self._check_boundary_and_layers()

    @property
    def refinementLevels(self):
        """refinementLevels for snappyHexMeshDict as (min, max)."""
        return self.__refinementLevels

    @refinementLevels.setter
    def refinementLevels(self, v):
        if not v:
            self.__refinementLevels = None
        else:
            self.__refinementLevels = tuple(v)

    @property
    def nSurfaceLayers(self):
        """Number of surface layers for snappyHexMeshDict addLayers."""
        return self.__nSurfaceLayers

    @nSurfaceLayers.setter
    def nSurfaceLayers(self, v):
        if not v:
            self.__nSurfaceLayers = None
        else:
            self.__nSurfaceLayers = int(v)
            self._check_boundary_and_layers()

    def _check_boundary_and_layers(self):

        try:
            if not self.nSurfaceLayers:
                return
        except AttributeError:
            # not initiated yet
            return
        else:
            if not self.boundary_condition:
                return
            if self.boundary_condition.type == 'patch':
                print('Warning: You are adding layers to a geometry of type "patch".\n'
                      'Layers are normally used only for "wall" boundaries.')


class BFBlockGeometry(BFGeometry):
    """Butterfly block geometry.

    Use this geometry to create geometries for blockMeshDict.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        face_indices: A flatten list of (a, b, c) for indices for each face.
        boundary_condition: Boundary condition for this geometry.
        border_vertices: List of lists of (x, y, z) values for each quad face of
            the geometry.
    """

    def __init__(self, name, vertices, face_indices, border_vertices,
                 boundary_condition=None):
        """Create Block Geometry."""
        BFGeometry.__init__(self, name, vertices, face_indices, None,
                            boundary_condition)
        self.__border_vertices = border_vertices

    @property
    def isBFBlockGeometry(self):
        """Return True for Butterfly block geometries."""
        return True

    @property
    def border_vertices(self):
        """Return list of border vertices."""
        return self.__border_vertices


def bf_geometry_from_stl_block(stl_block, convert_from_meters=1):
    """Create BFGeometry from an stl block as a string."""
    solid = read_ascii_string(stl_block)

    vertices = tuple(tuple(i * convert_from_meters for i in ver)
                     for ver in tuple(solid.vertices))

    origi_ver = tuple(solid.vertices)

    indices = tuple(tuple(origi_ver.index(ver) for ver in facet.vertices)
                    for facet in solid.facets)
    normals = tuple(facet.normal for facet in solid.facets)

    return BFGeometry(solid.name, vertices, indices, normals)


def bf_geometry_from_stl_file(filepath, convert_from_meters=1):
    """Return a tuple of BFGeometry from an stl file."""
    with open(filepath, 'rb') as f:
        line = ''.join(f.readlines())

    blocks = ('\nsolid{}'.format(t) if not t.startswith('solid') else '\n{}'.format(t)
              for t in line.split('\nsolid'))
    del(line)

    return tuple(bf_geometry_from_stl_block(b, convert_from_meters) for b in blocks)


def calculate_min_max_from_bf_geometries(geometries, x_axis=None):
    """Calculate maximum and minimum x, y, z for this geometry.

    Returns:
        (min_pt, max_pt)
    """
    if not x_axis or x_axis[0] == 1 and x_axis[1] == 0:
        min_pt = list(geometries[0].min)
        max_pt = list(geometries[0].max)

        for geo in geometries[1:]:
            for i in xrange(3):
                if geo.min[i] < min_pt[i]:
                    min_pt[i] = geo.min[i]

                if geo.max[i] > max_pt[i]:
                    max_pt[i] = geo.max[i]

        return min_pt, max_pt
    else:
        # calculate min and max for each geometry in new coordinates
        inf_p = float('+inf')
        inf_n = float('-inf')
        min_pt = [inf_p, inf_p, inf_p]
        max_pt = [inf_n, inf_n, inf_n]

        angle = angle_anitclockwise((1, 0, 0), x_axis)
        vertices = tuple(pts for geo in geometries
                         for pts in calculate_min_max(geo, angle))
        for v in vertices:
            for i in xrange(3):
                if v[i] < min_pt[i]:
                    min_pt[i] = v[i]
                elif v[i] > max_pt[i]:
                    max_pt[i] = v[i]

        return rotate((0, 0, 0), min_pt, angle), rotate((0, 0, 0), max_pt, angle)


def calculate_min_max(geometry, angle):
    """Calculate maximum and minimum x, y, z for input geometry.

    angle: Anticlockwise rotation angle of the new coordinates system.
    """
    # get list of vertices in the new coordinates system
    vertices = (rotate((0, 0, 0), v, -angle) for v in geometry.vertices)

    inf_p = float('+inf')
    inf_n = float('-inf')
    min_pt = [inf_p, inf_p, inf_p]
    max_pt = [inf_n, inf_n, inf_n]

    for v in vertices:
        for i in xrange(3):
            if v[i] < min_pt[i]:
                min_pt[i] = v[i]
            elif v[i] > max_pt[i]:
                max_pt[i] = v[i]

    # rotate them back to XY coordinates
    return min_pt, max_pt


def dimensions_from_min_max(min_pt, max_pt, x_axis=None):
    """Calculate width, length and height for input x_axis."""
    x_axis = x_axis or (1, 0, 0)
    angle = angle_anitclockwise((1, 0, 0), x_axis)
    min_pt = rotate((0, 0, 0), min_pt, -angle)
    max_pt = rotate((0, 0, 0), max_pt, -angle)

    width = max_pt[0] - min_pt[0]
    length = max_pt[1] - min_pt[1]
    height = max_pt[2] - min_pt[2]

    return width, length, height
