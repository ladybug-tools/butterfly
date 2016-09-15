"""BF geometry library."""
import os
from boundarycondition import BoundaryCondition


class _BFMesh(object):
    """Base mesh geometry.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        faceIndices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
    """

    def __init__(self, name, vertices, faceIndices, normals):
        """Init Butterfly mesh."""
        self.name = name

        self.__vertices = vertices
        self.__faceIndices = faceIndices
        self.__normals = normals

        assert len(self.__faceIndices) == len(self.__normals), \
            "Length of faceIndices (%d) " \
            "should be equal to Length of normals (%d)" % (
                len(self.__faceIndices), len(self.__normals))

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

    def toStlString(self):
        """Get STL definition for this surface as a string."""
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
            self.__vertices[faceInd[0]][0],
            self.__vertices[faceInd[0]][1],
            self.__vertices[faceInd[0]][2],
            self.__vertices[faceInd[1]][0],
            self.__vertices[faceInd[1]][1],
            self.__vertices[faceInd[1]][2],
            self.__vertices[faceInd[2]][0],
            self.__vertices[faceInd[2]][1],
            self.__vertices[faceInd[2]][2]
        ) for count, faceInd in enumerate(self.__faceIndices))

        return "{}\n{}\n{}".format(
            _hea, "\n".join(_bodyCollector), _tale
        )

    def writeToStl(self, folder):
        """Save BFFace to a stl file. File name will be self.name."""
        with open(os.path.join(folder, "{}.stl".format(self.name)), "wb") as outf:
            outf.write(self.toStlString())

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

    def __init__(self, name, vertices, faceIndices, normals,
                 boundaryCondition=None):
        """Init Butterfly geometry."""
        _BFMesh.__init__(self, name, vertices, faceIndices, normals)
        self.boundaryCondition = boundaryCondition

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
            bc = BoundaryCondition()

        assert hasattr(bc, 'isBoundaryCondition'), \
            '{} is not a Butterfly boundary condition.'.format(bc)

        self.__bc = bc


class BFBlockGeometry(BFGeometry):
    """Butterfly block geometry.

    Use this geometry to create geometries for blockMeshDict.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        faceIndices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
        boundaryCondition: Boundary condition for this geometry.
        borderVertices: List of lists of (x, y, z) values for each quad face of
            the geometry.
    """

    def __init__(self, name, vertices, faceIndices, normals, borderVertices,
                 boundaryCondition=None):
        """Create Block Geometry."""
        BFGeometry.__init__(self, name, vertices, faceIndices, normals,
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


if __name__ == '__main__':
    vertices = ((0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0))

    geo = BFGeometry(name='square', vertices=vertices,
                     faceIndices=((0, 1, 2), (0, 2, 3)),
                     normals=((0, 0, 1), (0, 0, 1)))

    print geo.toStlString()
