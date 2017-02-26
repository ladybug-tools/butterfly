# coding=utf-8
"""BlockMeshDict class."""
from .boundarycondition import BoundingBoxBoundaryCondition, EmptyBoundaryCondition
from .foamfile import FoamFile
import vectormath
from .grading import SimpleGrading, Grading, MultiGrading
from .parser import CppDictParser
from .geometry import BFGeometry
from math import sqrt, sin, cos, radians
from collections import OrderedDict


class BlockMeshDict(FoamFile):
    """BlockMeshDict."""

    __defaultValues = OrderedDict()
    __defaultValues['convertToMeters'] = 1
    __defaultValues['vertices'] = None
    __defaultValues['blocks'] = None
    __defaultValues['boundary'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='blockMeshDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

        self.__BFBlockGeometries = None  # this will be overwritten in classmethods
        self.__vertices = None
        self.__isFromVertices = False
        # variables for 2d blockMeshDict
        self.__is2dInXDir = False
        self.__is2dInYDir = False
        self.__is2dInZDir = False
        self.__original3dVertices = None

    @classmethod
    def fromFile(cls, filepah, convertToMeters=1):
        """Create a blockMeshDict from file.

        Args:
            filepah: Full path to blockMeshDict.
            converToMeters: converToMeters for the new document. This values
                will be used to update the vertices to the new units. Default
                is 1 which means blockMeshDict will be converted to meters.
        """
        _cls = cls()

        with open(filepah, 'rb') as bf:
            lines = CppDictParser._removeComments(bf.read())
            bmd = ' '.join(lines.replace('\r\n', ' ').replace('\n', ' ').split())

        _cls.values['convertToMeters'] = convertToMeters

        originalConvertToMeters = float(bmd.split('convertToMeters')[-1].split(';')[0])

        conversion = convertToMeters / originalConvertToMeters

        # find vertices
        vertices = list(eval(','.join(bmd.split('vertices')[-1]
                                      .split(';')[0]
                                      .strip()[1:-1]
                                      .split())))

        _cls.__vertices = list(tuple(i / conversion for i in v)
                               for v in vertices)

        # get blocks, order of vertices, nDivXYZ, grading
        blocks = bmd.split('blocks')[-1].split(';')[0].strip()
        xyz, simpleGrading = blocks.split('simpleGrading')

        _cls.__order, _cls.nDivXYZ = eval(','.join(xyz.split('hex')[-1].split()))

        simpleGrading = eval(','.join(simpleGrading.strip()[:-1]
                                      .replace('( ', '(')
                                      .replace(' )', ')')
                                      .split()))

        _cls.grading = SimpleGrading(
            *(MultiGrading(tuple(Grading(*i) for i in g))
              if isinstance(g, tuple) else Grading(g)
              for g in simpleGrading))

        # recreate boundary faces
        boundaryString = bmd.replace(' (', '(').replace(' )', ')') \
            .split('boundary(')[-1].strip().replace('});', '}') \
            .replace('));', ');').replace('((', ' (').replace(')(', ') (')

        _cls.values['boundary'] = {}
        for key, values in CppDictParser(boundaryString).values.iteritems():
            if isinstance(values, dict) and 'type' in values and 'faces' in values:
                values['faces'] = eval(str(values['faces']).replace(' ', ','))

                _cls.values['boundary'][key] = values

        del((lines, bmd))
        return _cls

    @classmethod
    def fromOriginAndSize(cls, origin, width, length, height, convertToMeters=1,
                          nDivXYZ=None, grading=None, xAxis=None):
        """Create BlockMeshDict from BFBlockGeometries.

        Args:
            origin: Minimum point of bounding box as (x, y, z).
            width: Width in x direction.
            length: Length in y direction.
            height: Height in y direction.
            convertToMeters: Scaling factor for the vertex coordinates.
            nDivXYZ: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            xAxis: An optional tuple that indicates the xAxis direction
                (default: (1, 0)).
        """
        _xAxis = vectormath.normalize((xAxis[0], xAxis[1], 0) if xAxis else (1, 0, 0))
        _zAxis = (0, 0, 1)
        _yAxis = vectormath.crossProduct(_zAxis, _xAxis)
        vertices = [
            vectormath.move(origin,
                            vectormath.sums((vectormath.scale(_xAxis, i * width),
                                             vectormath.scale(_yAxis, j * length),
                                             vectormath.scale(_zAxis, k * height))
                                            ))
            for i in range(2) for j in range(2) for k in range(2)]

        return cls.fromVertices(vertices, convertToMeters, nDivXYZ, grading,
                                xAxis)

    @classmethod
    def fromMinMax(cls, minPt, maxPt, convertToMeters=1, nDivXYZ=None, grading=None,
                   xAxis=None):
        """Create BlockMeshDict from minimum and maximum point.

        Args:
            minPt: Minimum point of bounding box as (x, y, z).
            maxPt: Maximum point of bounding box as (x, y, z).
            convertToMeters: Scaling factor for the vertex coordinates.
            nDivXYZ: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            xAxis: An optional tuple that indicates the xAxis direction
                (default: (1, 0)).
        """
        _xAxis = vectormath.normalize((xAxis[0], xAxis[1], 0) if xAxis else (1, 0, 0))
        _zAxis = (0, 0, 1)
        _yAxis = vectormath.crossProduct(_zAxis, _xAxis)
        diagonal2D = tuple(i - j for i, j in zip(maxPt, minPt))[:2]
        _angle = radians(vectormath.angleAnitclockwise(_xAxis[:2], diagonal2D))
        width = cos(_angle) * vectormath.length(diagonal2D)
        length = sin(_angle) * vectormath.length(diagonal2D)
        height = maxPt[2] - minPt[2]

        vertices = [
            vectormath.move(minPt,
                            vectormath.sums((vectormath.scale(_xAxis, i * width),
                                             vectormath.scale(_yAxis, j * length),
                                             vectormath.scale(_zAxis, k * height))
                                            ))

            for i in range(2) for j in range(2) for k in range(2)]

        return cls.fromVertices(vertices, convertToMeters, nDivXYZ, grading,
                                xAxis)

    @classmethod
    def fromVertices(cls, vertices, convertToMeters=1, nDivXYZ=None,
                     grading=None, xAxis=None):
        """Create BlockMeshDict from vertices.

        Args:
            vertices: 8 vertices to define the bounding box.
            convertToMeters: Scaling factor for the vertex coordinates.
            nDivXYZ: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            xAxis: An optional tuple that indicates the xAxis direction
                (default: (1, 0)).
        """
        _cls = cls()
        _cls.values['convertToMeters'] = convertToMeters
        _cls.__rawvertices = vertices

        # sort vertices
        _cls.xAxis = xAxis[:2] if xAxis else (1, 0)

        _cls.__vertices = _cls.__sortVertices()

        _cls.__order = tuple(range(8))

        # update self.values['boundary']
        _cls.__updateBoundaryFromSortedVertices()

        _cls.nDivXYZ = nDivXYZ

        # assign grading
        _cls.grading = grading
        _cls.__isFromVertices = True
        return _cls

    @classmethod
    def fromBFBlockGeometries(cls, BFBlockGeometries, convertToMeters=1,
                              nDivXYZ=None, grading=None, xAxis=None):
        """Create BlockMeshDict from BFBlockGeometries.

        Args:
            BFBlockGeometries: A collection of boundary surfaces for bounding box.
            convertToMeters: Scaling factor for the vertex coordinates.
            nDivXYZ: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            xAxis: An optional tuple that indicates the xAxis direction
                (default: (1, 0)).
        """
        _cls = cls()
        _cls.values['convertToMeters'] = convertToMeters
        _cls.__BFBlockGeometries = BFBlockGeometries

        try:
            # collect uniqe vertices from all BFGeometries
            _cls.__rawvertices = tuple(
                set(v for f in _cls.__BFBlockGeometries
                    for vgroup in f.borderVertices
                    for v in vgroup))
        except AttributeError as e:
            raise TypeError('At least one of the input geometries is not a '
                            'Butterfly block geometry:\n\t{}'.format(e))

        # sort vertices
        _cls.xAxis = xAxis[:2] if xAxis else (1, 0)
        _cls.__vertices = _cls.__sortVertices()

        # update self.values['boundary']
        _cls.__updateBoundaryFromBFBlockGeometries()

        _cls.__order = tuple(range(8))

        _cls.nDivXYZ = nDivXYZ

        # assign grading
        _cls.grading = grading

        return _cls

    @property
    def convertToMeters(self):
        """Get convertToMeters."""
        return self.values['convertToMeters']

    @property
    def boundary(self):
        """Get boundaries and a dictionary."""
        return self.values['boundary']

    @property
    def is2dInXDirection(self):
        """Return True if the case is 2d in X direction."""
        return self.__is2dInXDir

    @property
    def is2dInYDirection(self):
        """Return True if the case is 2d in Y direction."""
        return self.__is2dInYDir

    @property
    def is2dInZDirection(self):
        """Return True if the case is 2d in Z direction."""
        return self.__is2dInZDir

    @property
    def vertices(self):
        """Get the sorted list of vertices."""
        return self.__vertices

    def updateVertices(self, vertices, xAxis=None):
        """Update blockMeshDict vertices."""
        self.__rawvertices = vertices

        # sort vertices
        self.xAxis = xAxis[:2] if xAxis else (1, 0)

        self.__vertices = self.__sortVertices()

        self.__order = tuple(range(8))

        # update self.values['boundary']
        self.__updateBoundaryFromSortedVertices()

    @property
    def verticesOrder(self):
        """Get order of vertices in blocks."""
        return self.__order

    @property
    def geometry(self):
        """A tuple of BFGeometries for BoundingBox faces."""
        def __getBFGeometry(name, attr):
            if name == 'boundingbox_empty':
                bc = EmptyBoundaryCondition()
            else:
                bc = BoundingBoxBoundaryCondition()

            ind = attr['faces'] if hasattr(attr['faces'][0], '__iter__') else \
                (attr['faces'],)

            # unique indecies
            uniuqe = tuple(set(i for inx in ind for i in inx))

            renumberedIndx = tuple(tuple(uniuqe.index(i) for i in inx)
                                   for inx in ind)

            return BFGeometry(name, tuple(self.vertices[i] for i in uniuqe),
                              renumberedIndx, boundaryCondition=bc)

        if not self.__BFBlockGeometries:
            self.__BFBlockGeometries = tuple(
                __getBFGeometry(name, attr)
                for name, attr in self.boundary.iteritems())

        return self.__BFBlockGeometries

    @property
    def width(self):
        """Length of block in X direction."""
        return self.__distance(self.vertices[self.verticesOrder[0]],
                               self.vertices[self.verticesOrder[1]])

    @property
    def length(self):
        """Length of block in Y direction."""
        return self.__distance(self.vertices[self.verticesOrder[0]],
                               self.vertices[self.verticesOrder[3]])

    @property
    def height(self):
        """Length of block in Z direction."""
        return self.__distance(self.vertices[self.verticesOrder[0]],
                               self.vertices[self.verticesOrder[4]])

    @property
    def center(self):
        """Get center of the block."""
        return self.__averageVerices()

    @property
    def minZ(self):
        """Return minimum Z value of vertices in this block."""
        return self.vertices[self.verticesOrder[0]][2]

    @property
    def nDivXYZ(self):
        """Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5)."""
        return self.__nDivXYZ

    @nDivXYZ.setter
    def nDivXYZ(self, dXYZ):
        self.__nDivXYZ = tuple(int(v) for v in dXYZ) if dXYZ else (5, 5, 5)
        if self.__is2dInXDir:
            self.__nDivXYZ = 1, self.__nDivXYZ[1], self.__nDivXYZ[2]
        elif self.__is2dInYDir:
            self.__nDivXYZ = self.__nDivXYZ[0], 1, self.__nDivXYZ[2]
        elif self.__is2dInZDir:
            self.__nDivXYZ = self.__nDivXYZ[0], self.__nDivXYZ[1], 1

    @property
    def grading(self):
        """A simpleGrading (default: simpleGrading(1, 1, 1))."""
        return self.__grading

    @grading.setter
    def grading(self, g):
        self.__grading = g if g else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simpleGrading.'.format(g)

    def make3d(self):
        """Reload the 3d blockMeshDict if it has been converted to 2d."""
        if not self.__original3dVertices:
            print('This blockMeshDict is already a 3d blockMeshDict.')
            return
        self.__vertices = self.__original3dVertices
        self.__is2dInXDir = False
        self.__is2dInYDir = False
        self.__is2dInZDir = False

    def make2d(self, planeOrigin, planeNormal, width=0.1):
        """Make the blockMeshDict two dimensional.

        Args:
            planeOrigin: Plane origin as (x, y, z).
            planeNormal: Plane normal as (x, y, z).
            width: width of 2d blockMeshDict (default: 01).
        """
        # copy original vertices
        if not self.__original3dVertices:
            self.__original3dVertices = self.vertices
        else:
            # load original 3d vertices
            self.make3d()

        n = vectormath.normalize(planeNormal)

        # project all vertices to plane and move them in direction of normal
        # by half of width
        self.__vertices = [
            self.__calculate2dPoints(v, planeOrigin, n, width)
            for v in self.vertices]

        # set boundary condition to empty
        # and number of divisions to 1 in shortest side
        minimum = min(self.width, self.length, self.height)
        if self.width == minimum:
            self.nDivXYZ = (1, self.nDivXYZ[1], self.nDivXYZ[2])
            self.__is2dInXDir = True
            # set both sides to empty
            self.__setBoundaryToEmpty(4)
            self.__setBoundaryToEmpty(5)

        elif self.length == minimum:
            self.nDivXYZ = (self.nDivXYZ[0], 1, self.nDivXYZ[2])
            self.__is2dInYDir = True
            # set inlet and outlet to empty
            self.__setBoundaryToEmpty(0)
            self.__setBoundaryToEmpty(1)

        elif self.height == minimum:
            self.nDivXYZ = (self.nDivXYZ[0], self.nDivXYZ[1], 1)
            self.__is2dInZDir = True
            # set top and bottom to empty
            self.__setBoundaryToEmpty(2)
            self.__setBoundaryToEmpty(3)

    def expandUniformByCellsCount(self, count, renumberDivision=True):
        """Expand blockMeshDict boundingbox for n cells from all sides.

        This method will increase the number of divisions by 2 to keep the size
        of the cells unchanged unless renumberDivision is set to False. Use a
        negative count to shrink the bounding box.
        """
        x, y, z = self.nDivXYZ
        self.expandX((self.width / float(x)) * count)
        self.expandY((self.length / float(y)) * count)
        self.expandZ((self.height / float(z)) * count)
        if renumberDivision:
            self.nDivXYZ = (x + 2 * count, y + 2 * count, z + 2 * count)

    def expandByCellsCount(self, xCount, yCount, zCount, renumberDivision=True):
        """Expand blockMeshDict boundingbox for n cells from all sides.

        This method will increase the number of divisions by 2 to keep the size
        of the cells unchanged unless renumberDivision is set to False. Use a
        negative count to shrink the bounding box.
        """
        x, y, z = self.nDivXYZ
        self.expandX((self.width / float(x)) * xCount)
        self.expandY((self.length / float(y)) * yCount)
        self.expandZ((self.height / float(z)) * zCount)
        if renumberDivision:
            self.nDivXYZ = (x + 2 * xCount, y + 2 * yCount, z + 2 * zCount)

    def expandUniform(self, dist):
        """Expand blockMeshDict boundingbox for dist in all directions."""
        if not dist:
            return
        self.expandX(dist)
        self.expandY(dist)
        self.expandZ(dist)

    def expandX(self, dist):
        """Expand blockMeshDict boundingbox for dist in x and -x directions."""
        _xAxis = (self.xAxis[0], self.xAxis[1], 0) if len(self.xAxis) == 2 \
            else self.xAxis

        for i in (0, 3, 7, 4):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_xAxis, -dist))

        for i in (1, 2, 6, 5):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_xAxis, dist))

    def expandY(self, dist):
        """Expand blockMeshDict boundingbox for dist in y and -y directions."""
        _zAxis = (0, 0, 1)
        _yAxis = vectormath.crossProduct(_zAxis, self.xAxis)
        for i in (0, 1, 5, 4):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_yAxis, -dist))

        for i in (3, 2, 6, 7):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_yAxis, dist))

    def expandZ(self, dist):
        """Expand blockMeshDict boundingbox for dist in z and -z directions."""
        _zAxis = (0, 0, 1)
        for i in (0, 1, 2, 3):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_zAxis, -dist))

        for i in (4, 5, 6, 7):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_zAxis, dist))

    @staticmethod
    def __calculate2dPoints(v, o, n, w):
        # project point
        p = vectormath.project(v, o, n)
        # move the projected point backwards for half of the width
        t = vectormath.scale(vectormath.normalize(vectormath.subtract(v, p)),
                             w / 2.0)
        return vectormath.move(p, t)

    def nDivXYZByCellSize(self, cellSizeXYZ):
        """Set number of divisions by cell size."""
        x, y, z = cellSizeXYZ
        self.nDivXYZ = int(round(self.width / x)), int(round(self.length / y)), \
            int(round(self.height / z))

    def updateMeshingParameters(self, meshingParameters):
        """Update meshing parameters for blockMeshDict."""
        if not meshingParameters:
            return

        assert hasattr(meshingParameters, 'isMeshingParameters'), \
            'Expected MeshingParameters not {}'.format(type(meshingParameters))

        if meshingParameters.cellSizeXYZ:
            self.nDivXYZByCellSize(meshingParameters.cellSizeXYZ)

        if meshingParameters.grading:
            self.grading = meshingParameters.grading

    @property
    def bottomFaceIndices(self):
        """Get indecies for bottom face."""
        return (self.verticesOrder[0], self.verticesOrder[3],
                self.verticesOrder[2], self.verticesOrder[1])

    @property
    def topFaceIndices(self):
        """Get indecies for top face."""
        return (self.verticesOrder[4], self.verticesOrder[5],
                self.verticesOrder[6], self.verticesOrder[7])

    @property
    def rightFaceIndices(self):
        """Get indecies for right face."""
        return (self.verticesOrder[1], self.verticesOrder[2],
                self.verticesOrder[6], self.verticesOrder[5])

    @property
    def leftFaceIndices(self):
        """Get indecies for left face."""
        return (self.verticesOrder[3], self.verticesOrder[0],
                self.verticesOrder[4], self.verticesOrder[7])

    @property
    def frontFaceIndices(self):
        """Get indecies for front face."""
        return (self.verticesOrder[0], self.verticesOrder[1],
                self.verticesOrder[5], self.verticesOrder[4])

    @property
    def backFaceIndices(self):
        """Get indecies for back face."""
        return (self.verticesOrder[2], self.verticesOrder[3],
                self.verticesOrder[7], self.verticesOrder[6])

    def getFaceIndices(self, faceIndex):
        """Update boundary to empty for one of the faces.

        Args:
            faceIndex: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        faceIndices = {0: self.frontFaceIndices, 1: self.backFaceIndices,
                       2: self.bottomFaceIndices, 3: self.topFaceIndices,
                       4: self.rightFaceIndices, 5: self.leftFaceIndices}

        return faceIndices[faceIndex]

    @property
    def bottomFaceVertices(self):
        """Get vertices for bottom face."""
        return tuple(self.vertices[o] for o in self.bottomFaceIndices)

    @property
    def topFaceVertices(self):
        """Get vertices for top face."""
        return tuple(self.vertices[o] for o in self.topFaceIndices)

    @property
    def rightFaceVertices(self):
        """Get vertices for right face."""
        return tuple(self.vertices[o] for o in self.rightFaceIndices)

    @property
    def leftFaceVertices(self):
        """Get vertices for left face."""
        return tuple(self.vertices[o] for o in self.leftFaceIndices)

    @property
    def frontFaceVertices(self):
        """Get vertices for front face."""
        return tuple(self.vertices[o] for o in self.frontFaceIndices)

    @property
    def backFaceVertices(self):
        """Get vertices for back face."""
        return tuple(self.vertices[o] for o in self.backFaceIndices)

    def getFaceVertices(self, faceIndex):
        """Update boundary to empty for one of the faces.

        Args:
            faceIndex: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        faceVertices = {0: self.frontFaceVertices, 1: self.backFaceVertices,
                        2: self.bottomFaceVertices, 3: self.topFaceVertices,
                        4: self.rightFaceVertices, 5: self.leftFaceVertices}

        return faceVertices[faceIndex]

    def __setBoundaryToEmpty(self, faceIndex):
        """Update boundary to empty for the face based on index.

        Args:
            faceIndex: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        # get indices and vertices for the faceIndex
        ind = self.getFaceIndices(faceIndex)

        if self.__isFromVertices:
            if 'boundingbox_empty' not in self.values['boundary']:
                self.values['boundary']['boundingbox_empty'] = \
                    {'type': 'empty', 'faces': ()}

            self.values['boundary']['boundingbox_empty']['faces'] += (ind,)
            self.values['boundary']['boundingbox']['faces'] = tuple(
                o for o in self.values['boundary']['boundingbox']['faces']
                if o != ind
            )
        else:
            # update boundary condition for the geometry if the boundary is created
            # from geometry
            for name, v in self.values['boundary'].iteritems():
                if ind in v['faces']:
                    v['type'] = 'empty'

                    for geo in self.__BFBlockGeometries:
                        if geo.name == name:
                            geo.boundaryCondition = EmptyBoundaryCondition()
                    break

    def __updateBoundaryFromSortedVertices(self):
        """Update boundary dictionary based ordered vertices."""
        self.values['boundary']['boundingbox'] = {
            'type': 'wall',
            'faces': (self.bottomFaceIndices, self.topFaceIndices,
                      self.rightFaceIndices, self.leftFaceIndices,
                      self.frontFaceIndices, self.backFaceIndices,
                      )
        }

    def __updateBoundaryFromBFBlockGeometries(self):
        """Update boundary dictionary based on BFBlockGeometries input."""
        for geo in self.__BFBlockGeometries:
            try:
                self.values['boundary'][geo.name] = {
                    'type': geo.boundaryCondition.type,
                    'faces': tuple(tuple(self.vertices.index(v) for v in verGroup)
                                   for verGroup in geo.borderVertices)
                }
            except AttributeError as e:
                raise TypeError('Wrong input geometry!\n{}'.format(e))

    def __boundaryToOpenFOAM(self):
        _body = "   %s\n" \
                "   {\n" \
                "       type %s;\n" \
                "       faces\n" \
                "       (" \
                "       %s\n" \
                "       );\n" \
                "   }\n"

        col = (_body % (name, attr['type'],
                        '\n' + '\n'.join('\t' + str(indices).replace(",", "")
                                         for indices in attr['faces']))
               if isinstance(attr['faces'][0], tuple) else
               _body % (name, attr['type'],
                        '\n\t' + str(attr['faces']).replace(",", ""))
               for name, attr in self.boundary.iteritems())

        return 'boundary\n(%s);\n' % '\n'.join(col)

    @staticmethod
    def __distance(v1, v2):
        return sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))

    def __averageVerices(self):
        _x, _y, _z = 0, 0, 0

        for ver in self.__rawvertices:
            _x += ver[0]
            _y += ver[1]
            _z += ver[2]

        numofver = len(self.__rawvertices)
        return _x / numofver, _y / numofver, _z / numofver

    def __sortVertices(self):
        """sort input vertices."""
        groups = {}
        for p in self.__rawvertices:
            if p[2] not in groups:
                groups[p[2]] = []

            groups[p[2]].append((p[0], p[1]))

        zValues = groups.keys()
        zValues.sort()
        pointGroups = groups.values()

        assert len(zValues) == 2, \
            'Number of Z values must be 2 not {}: {}.'.format(len(zValues),
                                                              zValues)

        for g in pointGroups:
            assert len(g) == 4

        # the points in both height are identical so I just take the first group
        # and sort them
        xAxisReversed = (-self.xAxis[0], -self.xAxis[1])
        centerPt = self.center[:2]
        sortedPoints2d = \
            sorted(pointGroups[0],
                   key=lambda x: vectormath.angleAnitclockwise(
                       xAxisReversed, tuple(c1 - c2 for c1, c2
                                            in zip(x, centerPt))))

        sortedPoints = [(pt[0], pt[1], z) for z in zValues for pt in sortedPoints2d]
        return sortedPoints

    def toOpenFOAM(self):
        """Return OpenFOAM representation as a string."""
        _hea = self.header()
        _body = "\nconvertToMeters %.4f;\n" \
                "\n" \
                "vertices\n" \
                "(\n\t%s\n);\n" \
                "\n" \
                "blocks\n" \
                "(\nhex %s %s %s\n);\n" \
                "\n" \
                "edges\n" \
                "(%s);\n" \
                "\n" \
                "%s" \
                "\n" \
                "mergePatchPair\n" \
                "(%s);\n"

        return _hea + \
            _body % (
                self.convertToMeters,
                "\n\t".join(tuple(str(ver).replace(",", "")
                                  for ver in self.vertices)),
                str(self.verticesOrder).replace(",", ""),
                str(self.nDivXYZ).replace(",", ""),
                self.grading,  # blocks
                "\n",  # edges
                self.__boundaryToOpenFOAM(),  # boundary
                "\n")  # merge patch pair

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """BlockMeshDict representation."""
        return self.toOpenFOAM()
