# coding=utf-8
"""BF Grasshopper geometry library."""
try:
    import Rhino as rc
    from scriptcontext import doc
except ImportError:
    pass

from copy import deepcopy
from ..geometry import BFGeometry


class GHMesh(object):
    """Base mesh class for Butterf Grasshopper.

    Attributes:
        geometries: A list of Grasshopper meshes or Breps. All input geometries
            will be converted as a joined mesh.
        meshingParameters: Grasshopper meshing parameters for meshing brep geometries.
            In case geometry is Mesh this input won't be used.
    """

    def __init__(self, geometries, meshingParameters=None):
        """Init Butterfly geometry in Grasshopper."""
        if not meshingParameters:
            meshingParameters = rc.Geometry.MeshingParameters.Default

        self.__meshingParameters = meshingParameters
        self.geometry = geometries

    @property
    def geometry(self):
        """Mesh geometry of the geometry."""
        return self.__geometry

    @geometry.setter
    def geometry(self, geo):
        """Geometry.

        Args:
            geo: A list of geometries
        """
        _geo = rc.Geometry.Mesh()

        # if geo is not a mesh try to mesh it
        # this is useful for creating stl files
        for g in geo:
            if isinstance(g, rc.Geometry.Brep):
                for m in rc.Geometry.Mesh.CreateFromBrep(g, self.__meshingParameters):
                    _geo.Append(m)
            elif isinstance(g, rc.Geometry.Mesh):
                _geo.Append(g)
            else:
                raise ValueError("Input geometry should be Mesh or Brep not {}"
                                 .format(type(g)))

        self.__geometry = self.__triangulateMesh(_geo)

    def __triangulateMesh(self, mesh):
        """Triangulate Rhino Mesh."""
        triMesh = rc.Geometry.Mesh()

        for i in xrange(mesh.Vertices.Count):
            triMesh.Vertices.Add(mesh.Vertices[i])

        for face in mesh.Faces:
            triMesh.Faces.AddFace(face.A, face.B, face.C)
            if face.IsQuad:
                triMesh.Faces.AddFace(face.A, face.C, face.D)

        # collect mesh faces, normals and indices
        triMesh.FaceNormals.ComputeFaceNormals()
        triMesh.FaceNormals.UnitizeFaceNormals()

        self.normals = tuple((n.X, n.Y, n.Z) for n in triMesh.FaceNormals)
        self.vertices = tuple((v.X, v.Y, v.Z) for v in triMesh.Vertices)
        # indices
        self.faceIndices = tuple((f.A, f.B, f.C) for f in triMesh.Faces)
        return triMesh

    def duplicate(self):
        """Return a copy of GHMesh."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """GHMesh."""
        return str(self.geometry)


class GHBFGeometry(BFGeometry):
    """Base geometry class for Butterfly.

    Attributes:
        name: Name as a string (A-Z a-z 0-9).
        geometries: A list of Grasshopper meshes or Breps. All input geometries
            will be converted as a joined mesh.
        boundaryCondition: Boundary condition for this geometry
        meshingParameters: Grasshopper meshing parameters for meshing brep geometries.
            In case geometry is Mesh this input won't be used.
    """

    def __init__(self, name, geometries, boundaryCondition=None,
                 meshingParameters=None):
        """Init Butterfly geometry in Grasshopper."""
        # convert input geometries to a butterfly GHMesh.
        _mesh = GHMesh(geometries, meshingParameters)

        self.__geometry = _mesh.geometry

        BFGeometry.__init__(self, name, _mesh.vertices, _mesh.faceIndices,
                            _mesh.normals, boundaryCondition)

    @property
    def geometry(self):
        """Mesh geometry of the geometry."""
        return self.__geometry


class GHBFBlockGeometry(GHBFGeometry):
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

    def __init__(self, name, geometries, boundaryCondition=None,
                 meshingParameters=None):
        """Init Butterfly block geometry in Grasshopper."""
        GHBFGeometry.__init__(self, name, geometries, boundaryCondition,
                              meshingParameters)

        self.__calculateBlockBorderVertices(geometries)

    @property
    def isBFBlockGeometry(self):
        """Return True for Butterfly block geometries."""
        return True

    @property
    def borderVertices(self):
        """Return list of border vertices."""
        return self.__borderVertices

    def __calculateBlockBorderVertices(self, geo):
        """Get list of border vertices."""
        self.__borderVertices = []
        for g in geo:
            if not isinstance(g, rc.Geometry.Brep):
                raise TypeError('{} is not a Brep.'.format(g))

            self.__borderVertices.extend(
                tuple(tuple((v.X, v.Y, v.Z) for v in self.__getFaceBorderVertices(f))
                      for f in g.Faces)
            )

    @staticmethod
    def __getFaceBorderVertices(face):
        """Get border vertices."""
        srf = face.DuplicateFace(doc.ModelAbsoluteTolerance)
        edgesJoined = rc.Geometry.Curve.JoinCurves(srf.DuplicateEdgeCurves(True))
        return (e.PointAtStart for e in edgesJoined[0].DuplicateSegments())

    def toBlockMeshDict(self, vertices):
        """Get blockMeshDict string for this geometry.

        Args:
            vertices: list of vertices for all the geometries in the case.
        """
        _body = "   %s\n" \
                "   {\n" \
                "       type %s;\n" \
                "       faces\n" \
                "       (\n" \
                "%s\n" \
                "       );\n" \
                "   }\n"

        if not self.borderVertices:
            raise TypeError("This Butterfly geometry is created from meshes "
                            "and can't be expoerted as blockMeshDict.")

        try:
            renumberedIndices = (tuple(vertices.index(v) for v in verGroup)
                                 for verGroup in self.borderVertices)
        except:
            raise ValueError("Can't find the vertex "
                             "in the vertices:\ninput: {}\n vertices: {}"
                             .format(self.borderVertices, vertices))

        return _body % (
            self.name,
            self.boundaryCondition.type,
            "\n".join(["            " + str(indices).replace(",", "")
                       for indices in renumberedIndices])
        )
