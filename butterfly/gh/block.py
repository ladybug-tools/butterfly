"""Butterfly Block for Grasshopper."""
from ..block import Block


class GHBlock(Block):
    """Block in blockMeshDict.

    Args:
        box: A Box that represents block boundary.
        cellSizeXYZ: Size of cell in X, Y and Z directions in Rhino model units
            as a tuple.
        grading: grading as (x, y, z) (default: (1, 1, 1))
    """

    def __init__(self, box, cellSizeXYZ=None, grading=None):
        """Init Block class."""
        self.cellSizeXYZ = tuple(cellSizeXYZ) if cellSizeXYZ else (5, 5, 5)

        nDivXYZ = \
            int(round(box.X.Length / self.cellSizeXYZ[0])), \
            int(round(box.Y.Length / self.cellSizeXYZ[1])), \
            int(round(box.Z.Length / self.cellSizeXYZ[2]))

        vertices = self._calculateVertices(box.ToBrep())

        Block.__init__(self, vertices, nDivXYZ, grading)

    @property
    def minZ(self):
        """Return minimum Z value of vertices in this block."""
        _minZ = float('inf')

        for ver in self.vertices:
            if ver[2] < _minZ:
                _minZ = ver[2]

        return _minZ

    def _calculateVertices(self, geo):
        # sort faces based on Z value
        faces = sorted(geo.Faces, key=lambda f: self._cenPt(f).Z)

        return tuple((ver.Location.X, ver.Location.Y, ver.Location.Z)
                     for verGroup in
                     (self._shiftVertices(faces[0].ToBrep().Vertices),
                     faces[-1].ToBrep().Vertices)
                     for ver in verGroup)

    @staticmethod
    def _shiftVertices(vertices):
        """Shift vertices to match openfoam order."""
        _ver = list(vertices)
        _ver.reverse()
        return _ver[-1:] + _ver[:-1]

    @staticmethod
    def _cenPt(f):
        """Calculate center point for a grasshopper face."""
        return f.PointAt((f.Domain(0).Min + f.Domain(0).Max) / 2,
                         (f.Domain(1).Min + f.Domain(1).Max) / 2)
