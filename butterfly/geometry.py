# coding=utf-8
"""BF geometry library."""
import os
from copy import deepcopy
from .boundarycondition import IndoorWallBoundaryCondition
from .stl import read_ascii_string
from .vectormath import crossProduct, rotate, angleAnitclockwise


class _BFMesh(object):
    """Base mesh geometry.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        faceIndices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
    """

    def __init__(self, name, vertices, faceIndices, normals=None):
        """Init Butterfly mesh."""
        self.name = name

        self.__vertices = vertices
        self.__faceIndices = faceIndices

        if not normals:
            normals = self.__calculateNormals()

        self.__normals = normals

        assert len(self.__faceIndices) == len(self.__normals), \
            "Length of faceIndices (%d) " \
            "should be equal to Length of normals (%d)" % (
                len(self.__faceIndices), len(self.__normals))

        self.__calculateMinMax()

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
    def faceIndices(self):
        """A flatten list of (a, b, c) for indices for each face."""
        return self.__faceIndices

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

    def __calculateNormals(self):
        """Calculate normals from vertices."""
        return tuple(self.__calculateNormalFromPoints(
            tuple(self.vertices[i] for i in ind)) for ind in self.faceIndices)

    @staticmethod
    def __calculateNormalFromPoints(pts):
        """Calculate normal for three points."""
        # vector between first point and the second point on the list
        try:
            pt1, pt2, pt3 = pts[:3]
        except Exception as e:
            raise ValueError('Failed to calculate normal:\n\t{}'.format(e))

        v1 = (pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2])

        # vector between first point and the last point in the list
        v2 = (pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2])

        return crossProduct(v1, v2)

    def __calculateMinMax(self):
        """Calculate maximum and minimum x, y, z for this geometry."""
        minPt = list(self.vertices[0])
        maxPt = list(self.vertices[0])

        for v in self.vertices[1:]:
            for i in xrange(3):
                if v[i] < minPt[i]:
                    minPt[i] = v[i]
                elif v[i] > maxPt[i]:
                    maxPt[i] = v[i]

        self.__min = minPt
        self.__max = maxPt

    def toSTL(self, convertToMeters=1):
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
        ) for count, faceInd in enumerate(self.__faceIndices))

        return "{}\n{}\n{}\n".format(
            _hea, "\n".join(_bodyCollector), _tale
        )

    def writeToStl(self, folder, convertToMeters=1):
        """Save BFFace to a stl file. File name will be self.name.

        Args:
            convertToMeters: A value to scale the geometry to meters. For isinstance
                if the mesh is in mm the value should be 0.001 (default: 1).
        """
        with open(os.path.join(folder, "{}.stl".format(self.name)), "wb") as outf:
            outf.write(self.toSTL(convertToMeters))

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
        faceIndices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
        boundaryCondition: Boundary condition for this geometry.

    Usage:

        vertices = ((0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0))

        geo = BFGeometry(name='square', vertices=vertices,
                         faceIndices=((0, 1, 2), (0, 2, 3)),
                         normals=((0, 0, 1), (0, 0, 1)))

        print geo.toStlString()
    """

    def __init__(self, name, vertices, faceIndices, normals=None,
                 boundaryCondition=None, refinementLevels=None,
                 nSurfaceLayers=None):
        """Init Butterfly geometry."""
        _BFMesh.__init__(self, name, vertices, faceIndices, normals)
        self.boundaryCondition = boundaryCondition
        self.refinementLevels = refinementLevels
        self.nSurfaceLayers = nSurfaceLayers

    @property
    def isBFGeometry(self):
        """Return True for Butterfly geometries."""
        return True

    @property
    def boundaryCondition(self):
        """Boundary condition."""
        return self.__bc

    @boundaryCondition.setter
    def boundaryCondition(self, bc):
        if not bc:
            bc = IndoorWallBoundaryCondition()

        assert hasattr(bc, 'isBoundaryCondition'), \
            '{} is not a Butterfly boundary condition.'.format(bc)

        self.__bc = bc
        self._checkBoundaryAndLayers()

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
            self._checkBoundaryAndLayers()

    def _checkBoundaryAndLayers(self):

        try:
            if not self.nSurfaceLayers:
                return
        except AttributeError:
            # not initiated yet
            return
        else:
            if not self.boundaryCondition:
                return
            if self.boundaryCondition.type == 'patch':
                print('Warning: You are adding layers to a geometry of type "patch".\n'
                      'Layers are normally used only for "wall" boundaries.')


class BFBlockGeometry(BFGeometry):
    """Butterfly block geometry.

    Use this geometry to create geometries for blockMeshDict.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        faceIndices: A flatten list of (a, b, c) for indices for each face.
        boundaryCondition: Boundary condition for this geometry.
        borderVertices: List of lists of (x, y, z) values for each quad face of
            the geometry.
    """

    def __init__(self, name, vertices, faceIndices, borderVertices,
                 boundaryCondition=None):
        """Create Block Geometry."""
        BFGeometry.__init__(self, name, vertices, faceIndices, None,
                            boundaryCondition)
        self.__borderVertices = borderVertices

    @property
    def isBFBlockGeometry(self):
        """Return True for Butterfly block geometries."""
        return True

    @property
    def borderVertices(self):
        """Return list of border vertices."""
        return self.__borderVertices


def bfGeometryFromStlBlock(stlBlock, convertFromMeters=1):
    """Create BFGeometry from an stl block as a string."""
    solid = read_ascii_string(stlBlock)

    vertices = tuple(tuple(i * convertFromMeters for i in ver)
                     for ver in tuple(solid.vertices))

    origiVer = tuple(solid.vertices)

    indices = tuple(tuple(origiVer.index(ver) for ver in facet.vertices)
                    for facet in solid.facets)
    normals = tuple(facet.normal for facet in solid.facets)

    return BFGeometry(solid.name, vertices, indices, normals)


def bfGeometryFromStlFile(filepath, convertFromMeters=1):
    """Return a tuple of BFGeometry from an stl file."""
    with open(filepath, 'rb') as f:
        line = ''.join(f.readlines())

    blocks = ('\nsolid{}'.format(t) if not t.startswith('solid') else '\n{}'.format(t)
              for t in line.split('\nsolid'))
    del(line)

    return tuple(bfGeometryFromStlBlock(b, convertFromMeters) for b in blocks)


def calculateMinMaxFromBFGeometries(geometries, xAxis=None):
    """Calculate maximum and minimum x, y, z for this geometry.

    Returns:
        (minPt, maxPt)
    """
    if not xAxis or xAxis[0] == 1 and xAxis[1] == 0:
        minPt = list(geometries[0].min)
        maxPt = list(geometries[0].max)

        for geo in geometries[1:]:
            for i in xrange(3):
                if geo.min[i] < minPt[i]:
                    minPt[i] = geo.min[i]

                if geo.max[i] > maxPt[i]:
                    maxPt[i] = geo.max[i]

        return minPt, maxPt
    else:
        # calculate min and max for each geometry in new coordinates
        infP = float('+inf')
        infN = float('-inf')
        minPt = [infP, infP, infP]
        maxPt = [infN, infN, infN]

        angle = angleAnitclockwise((1, 0, 0), xAxis)
        vertices = tuple(pts for geo in geometries
                         for pts in calculateMinMax(geo, angle))
        for v in vertices:
            for i in xrange(3):
                if v[i] < minPt[i]:
                    minPt[i] = v[i]
                elif v[i] > maxPt[i]:
                    maxPt[i] = v[i]

        return rotate((0, 0, 0), minPt, angle), rotate((0, 0, 0), maxPt, angle)


def calculateMinMax(geometry, angle):
    """Calculate maximum and minimum x, y, z for input geometry.

    angle: Anticlockwise rotation angle of the new coordinates system.
    """
    # get list of vertices in the new coordinates system
    vertices = (rotate((0, 0, 0), v, -angle) for v in geometry.vertices)

    infP = float('+inf')
    infN = float('-inf')
    minPt = [infP, infP, infP]
    maxPt = [infN, infN, infN]

    for v in vertices:
        for i in xrange(3):
            if v[i] < minPt[i]:
                minPt[i] = v[i]
            elif v[i] > maxPt[i]:
                maxPt[i] = v[i]

    # rotate them back to XY coordinates
    return minPt, maxPt
