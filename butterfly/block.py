# coding=utf-8
"""Butterfly Block class for blockMeshDict."""
import math
from copy import deepcopy

from .grading import SimpleGrading


class Block(object):
    """Block in blockMeshDict.

    Args:
        vertices: List of ordered block vertices.
        nDivXYZ: Number of divisions in (x, y, z) as a tuple.
        grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
    """

    def __init__(self, vertices, nDivXYZ, grading):
        """Init Block class."""
        self.vertices = vertices
        self.nDivXYZ = tuple(int(v) for v in nDivXYZ) if nDivXYZ else (5, 5, 5)

        # assign grading
        self.grading = grading if grading else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simpleGrading.'.format(grading)

    @property
    def minZ(self):
        """Return minimum Z value of vertices in this block."""
        _minZ = float('inf')

        for ver in self.vertices:
            if ver[2] < _minZ:
                _minZ = ver[2]

        return _minZ

    def toBlockMeshDict(self, vertices, tolerance=0.001):
        """Get blockMeshDict string.

        Args:
            vertices: list of vertices for all the geometries in the case.
            tolerance: Distance tolerance between input vertices and blockMesh
                vertices.
        """
        _body = "   hex {} {} {}"

        indices = self._findIndices(vertices, tolerance)

        return _body.format(str(indices).replace(",", ""),
                            str(self.nDivXYZ).replace(",", ""),
                            self.grading)

    def _findIndices(self, vertices, tolerance=0.001):
        """Return list of indices for input vertices.

        Args:
            tolerance: Distance tolerance between input vertices and blockMesh
            vertices.
        """
        def distance(p1, p2):
            return math.sqrt(sum((x - y) ** 2 for x, y in zip(p1, p2)))

        def findIndex(v):
            for count, i in enumerate(vertices):
                if distance(i, v) <= tolerance:
                    return count
            raise ValueError("Can't find vertex {} in input vertices: {}"
                             .format(v, vertices))

        indices = tuple(vertices.index(v) if v in vertices else findIndex(v)
                        for v in self.vertices)
        return indices

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM blockMeshDict boundary."""
        return "blockMeshDict::Boundary: {} simpleGrading {}".format(
            str(self.nDivXYZ).replace(",", ""), str(self.grading).replace(",", ""))
