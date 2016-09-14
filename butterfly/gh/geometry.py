"""Base class for geometry."""
try:
    import Rhino as rc
    from scriptcontext import doc
except ImportError:
    pass

from ..geometry import BFGeometry


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
        """Init Butterfly surface in Grasshopper."""
        if not meshingParameters:
            meshingParameters = rc.Geometry.MeshingParameters.Default

        self.meshingParameters = meshingParameters
        self.geometry = geometries
        BFGeometry.__init__(self, name, self.meshVertices, self.meshFaceIndices,
                            self.faceNormals, boundaryCondition)

    @property
    def borderVertices(self):
        """Return a list of lists for (x, y, z) vertices."""
        return self.__borderVertices

    @property
    def geometry(self):
        """Mesh geometry of the surface."""
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
                for m in rc.Geometry.Mesh.CreateFromBrep(g, self.meshingParameters):
                    _geo.Append(m)
            elif isinstance(g, rc.Geometry.Mesh):
                _geo.Append(g)
            else:
                raise ValueError("Input geometry should be Mesh or Brep not {}"
                                 .format(type(g)))

        self.__geometry = self.triangulateMesh(_geo)

        # now get clean vertices for faces which is useful to create the case
        # by blocks
        self.__borderVertices = []
        for g in geo:
            if isinstance(g, rc.Geometry.Brep):
                self.__borderVertices.extend(
                    tuple(tuple((v.X, v.Y, v.Z) for v in self.getBorderVertices(f))
                          for f in g.Faces)
                )
            elif isinstance(g, rc.Geometry.Mesh):
                print "One of the input geometries is mesh."
                print "You can only use snappyHexMesh with this geometry."

    @staticmethod
    def getBorderVertices(face):
        """Get border vertices."""
        srf = face.DuplicateFace(doc.ModelAbsoluteTolerance)
        edgesJoined = rc.Geometry.Curve.JoinCurves(srf.DuplicateEdgeCurves(True))
        return (e.PointAtStart for e in edgesJoined[0].DuplicateSegments())

    def triangulateMesh(self, mesh):
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

        self.faceNormals = tuple((n.X, n.Y, n.Z) for n in triMesh.FaceNormals)
        self.meshVertices = tuple((v.X, v.Y, v.Z) for v in triMesh.Vertices)
        # indices
        self.meshFaceIndices = tuple((f.A, f.B, f.C) for f in triMesh.Faces)
        return triMesh

    def blockMeshDict(self, vertices):
        """Get blockMeshDict string.

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
            raise TypeError("This Butterfly surface is created from meshes "
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
