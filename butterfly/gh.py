# All Grasshopper functions and classes should be in this file
import os
try:
    import Rhino as rc
    from scriptcontext import doc
except ImportError:
    pass



class BFSurface(object):
    def __init__(self, name, geometry, boundaryCondition=None,
                 meshingParameters=None):
        if not meshingParameters:
            meshingParameters = rc.Geometry.MeshingParameters.Default

        self.meshingParameters = meshingParameters
        self.name = name
        self.geometry = geometry
        # TODO: add check for boundary condition to be valid
        self.boundaryCondition = boundaryCondition

    @property
    def geometry(self):
        """Mesh geometry of the surface."""
        return self.__geometry

    @property
    def borderVertices(self):
        """Return a list of lists for (x, y, z) vertices."""
        return self.__borderVertices

    @geometry.setter
    def geometry(self, geo):
        """
        geo is a list of geometries
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
                print "One of the input geometries are mesh."
                print "You can only use snappyHexMesh with this geometry."

    @staticmethod
    def getBorderVertices(face):
        srf = face.DuplicateFace(doc.ModelAbsoluteTolerance)
        edgesJoined = rc.Geometry.Curve.JoinCurves(srf.DuplicateEdgeCurves(True))
        return (e.PointAtStart for e in edgesJoined[0].DuplicateSegments())

    def triangulateMesh(self, mesh):
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

    def blockMeshDict(self, vertices):
        """Get blockMeshDict string.

        Args:
            vertices: list of vertices for all the geometries in the case.
                This method should be moved under the case class.
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
            raise TypeError("This Butterfly surface is created from meshes " \
                            "and can't be expoerted as blockMeshDict.")

        try:
            renumberedIndices = (tuple(vertices.index(v) for v in verGroup)
                                 for verGroup in self.borderVertices)
        except:
            raise ValueError("Can't find the vertex " \
                             "in the vertices:\ninput: {}\n vertices: {}"
                             .format(self.borderVertices, vertices))


        return _body % (
                    self.name,
                    self.boundaryCondition,
                    "\n".join(["            " + str(indices).replace(",", "")
                               for indices in renumberedIndices])
        )

    def toStlString(self):
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
            self.normals[count][0],
            self.normals[count][1],
            self.normals[count][2],
            self.vertices[faceInd[0]][0],
            self.vertices[faceInd[0]][1],
            self.vertices[faceInd[0]][2],
            self.vertices[faceInd[1]][0],
            self.vertices[faceInd[1]][1],
            self.vertices[faceInd[1]][2],
            self.vertices[faceInd[2]][0],
            self.vertices[faceInd[2]][1],
            self.vertices[faceInd[2]][2]
        ) for count, faceInd in enumerate(self.faceIndices))

        return "{}\n{}\n{}".format(
                _hea,
                "\n".join(_bodyCollector),
                _tale)

    def writeToStl(self, folder):
        """Save BFFace to a stl file. File name will be self.name."""
        with open(os.path.join(folder, "{}.stl".format(self.name)), "wb") as outf:
            outf.write(self.toStlString())

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "BFSurface:{}".format(self.name)


class Block(object):
    """Block in blockMeshDict.

    Args:
        geometry: A closed brep that represents block boundary.
    """
    def __init__(self, geometry, nDiv, grading):
        self.vertices = self.calculateVertices(geometry)
        self.nDiv = tuple(int(v) for v in nDiv)
        self.grading = tuple(grading)

    def calculateVertices(self, geo):
        # sort faces based on Z value
        faces = sorted(geo.Faces, key=lambda f: self._cenPt(f).Z)

        return tuple((ver.Location.X, ver.Location.Y, ver.Location.Z) for verGroup in
                    (self.shiftVertices(faces[0].ToBrep().Vertices),
                     faces[-1].ToBrep().Vertices)
                     for ver in verGroup)

    @staticmethod
    def shiftVertices(vertices):
        # shift vertices to match openfoam order
        _ver = list(vertices)
        _ver.reverse()
        return _ver[-1:] + _ver[:-1]

    @staticmethod
    def _cenPt(f):
        return f.PointAt((f.Domain(0).Min + f.Domain(0).Max)/2,
                        (f.Domain(1).Min + f.Domain(1).Max)/2)

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
            raise ValueError("Can't find the vertex " \
                             "in the vertices:\ninput: {}\n vertices: {}"
                             .format(self.vertices, vertices))


        return _body.format(str(indices).replace(",", ""),
                            str(self.nDiv).replace(",", ""),
                            str(self.grading).replace(",", ""))


    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "Boundary: {} simpleGrading {}".format(str(self.nDiv).replace(",", ""),
                                                      str(self.grading).replace(",", ""))
