"""BF Surface for Grasshopper."""


# TODO: Write Block class with no Grasshopper dependencies
class Block(object):
    """Block in blockMeshDict.

    Args:
        geometry: A closed brep that represents block boundary.
    """

    def __init__(self, geometry, nDiv, grading):
        """Init Block class."""
        self.vertices = self.__calculateVertices(geometry)
        self.nDiv = tuple(int(v) for v in nDiv)
        self.grading = tuple(grading)

    @property
    def minZ(self):
        """Return minimum Z value of vertices in this block."""
        _minZ = float('inf')

        for ver in self.vertices:
            if ver[2] < _minZ:
                _minZ = ver[2]

        return _minZ

    def __calculateVertices(self, geo):
        # sort faces based on Z value
        faces = sorted(geo.Faces, key=lambda f: self._cenPt(f).Z)

        return tuple((ver.Location.X, ver.Location.Y, ver.Location.Z)
                     for verGroup in
                     (self.shiftVertices(faces[0].ToBrep().Vertices),
                     faces[-1].ToBrep().Vertices)
                     for ver in verGroup)

    @staticmethod
    def shiftVertices(vertices):
        """Shift vertices to match openfoam order."""
        _ver = list(vertices)
        _ver.reverse()
        return _ver[-1:] + _ver[:-1]

    @staticmethod
    def _cenPt(f):
        """Calculate center point for a grasshopper face."""
        return f.PointAt((f.Domain(0).Min + f.Domain(0).Max) / 2,
                         (f.Domain(1).Min + f.Domain(1).Max) / 2)

    def blockMeshDict(self, vertices):
        """Get blockMeshDict string.

        Args:
            vertices: list of vertices for all the geometries in the case.
                This method should be moved under the case class.
        """
        _body = "   hex {} {} simpleGrading {}"

        try:
            indices = tuple(vertices.index(v) for v in self.vertices)
        except ValueError:
            raise ValueError("Can't find the vertex "
                             "in the vertices:\ninput: {}\n vertices: {}"
                             .format(self.vertices, vertices))

        return _body.format(str(indices).replace(",", ""),
                            str(self.nDiv).replace(",", ""),
                            str(self.grading).replace(",", ""))

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM boundary."""
        return "Boundary: {} simpleGrading {}".format(str(self.nDiv).replace(",", ""),
                                                      str(self.grading).replace(",", ""))
