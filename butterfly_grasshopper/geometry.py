# coding=utf-8
"""BF Grasshopper geometry library."""
try:
    import Rhino as rc
    from scriptcontext import doc
except ImportError:
    pass

from copy import deepcopy
from butterfly.geometry import BFGeometry


class MeshGH(object):
    """Base mesh class for Butterfly Grasshopper.

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

    @property
    def normals(self):
        """Mesh Face normals."""
        return tuple((n.X, n.Y, n.Z) for n in self.geometry.FaceNormals)

    @property
    def vertices(self):
        """Mesh Face normals."""
        return tuple((v.X, v.Y, v.Z) for v in self.geometry.Vertices)

    @property
    def faceIndices(self):
        """Mesh Face Indices."""
        return tuple((f.A, f.B, f.C) for f in self.geometry.Faces)

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


class BFGeometryGH(BFGeometry):
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
                 refinementLevels=None, nSurfaceLayers=None,
                 meshingParameters=None):
        """Init Butterfly geometry in Grasshopper."""
        # convert input geometries to a butterfly GHMesh.
        _mesh = MeshGH(geometries, meshingParameters)

        self.__geometry = _mesh.geometry

        BFGeometry.__init__(self, name, _mesh.vertices, _mesh.faceIndices,
                            _mesh.normals, boundaryCondition, refinementLevels,
                            nSurfaceLayers)

    @property
    def geometry(self):
        """Mesh geometry of the geometry."""
        return self.__geometry


class BFBlockGeometry_GH(BFGeometryGH):
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
        BFGeometryGH.__init__(self, name, geometries, boundaryCondition,
                              meshingParameters=meshingParameters)

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


def BFMeshToMesh(bfMesh, color=None, scale=1):
    """convert a BFMesh object to Grasshopper mesh."""
    assert hasattr(bfMesh, 'vertices'), \
        '\t{} is not a valid BFMesh.'.format(bfMesh)
    assert hasattr(bfMesh, 'faceIndices'), \
        '\t{} is not a valid BFMesh.'.format(bfMesh)

    mesh = rc.Geometry.Mesh()
    for v in bfMesh.vertices:
        mesh.Vertices.Add(rc.Geometry.Point3d(*v))

    for face in bfMesh.faceIndices:
        mesh.Faces.AddFace(*face)

    if color:
        mesh.VertexColors.CreateMonotoneMesh(color)

    if scale != 1:
        mesh.Scale(scale)

    return mesh


def xyzToPoint(xyz, convertFromMeters=1):
    """Convert a xyz tuple to Point."""
    return rc.Geometry.Point3d(*(i * convertFromMeters for i in xyz))


def xyzToVector(xyz):
    """Convert a xyz tuple to Vector."""
    return rc.Geometry.Vector3d(*xyz)
