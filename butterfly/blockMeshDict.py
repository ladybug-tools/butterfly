# coding=utf-8
"""BlockMeshDict class."""
from .boundarycondition import BoundingBoxBoundaryCondition
from .foamfile import FoamFile
from .fields import Empty
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

        self.__BFBlockGeometries = None # this will be overwritten in classmethods
        self.__vertices = None

    @classmethod
    def fromFile(cls, filepah):
        """Create a blockMeshDict from file."""
        _cls = cls()

        with open(filepah, 'rb') as bf:
            lines = CppDictParser._removeComments(bf.read())
            bmd = ' '.join(lines.replace('\r\n', ' ').replace('\n', ' ').split())

        _cls.values['convertToMeters'] = \
            float(bmd.split('convertToMeters')[-1].split(';')[0])

        # find vertices
        _cls.__vertices = eval(','.join(bmd.split('vertices')[-1]
                                        .split(';')[0]
                                        .strip()[1:-1]
                                        .split()))

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
        vertices = tuple(
            vectormath.move(origin,
                            vectormath.sums((vectormath.scale(_xAxis, i *  width),
                                            vectormath.scale(_yAxis, j *  length),
                                            vectormath.scale(_zAxis, k *  height))
                            ))
            for i in range(2) for j in range(2) for k in range(2))

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

        vertices = tuple(
            vectormath.move(minPt,
                            vectormath.sums((vectormath.scale(_xAxis, i *  width),
                                            vectormath.scale(_yAxis, j *  length),
                                            vectormath.scale(_zAxis, k *  height))
                            ))
            for i in range(2) for j in range(2) for k in range(2))

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

        # update self.values['boundary']
        _cls.__updateBoundaryFromSortedVertices()

        _cls.__order = tuple(range(8))

        _cls.nDivXYZ = nDivXYZ

        # assign grading
        _cls.grading = grading

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
    def vertices(self):
        """Get the sorted list of vertices."""
        return self.__vertices

    @property
    def verticesOrder(self):
        """Get order of vertices in blocks."""
        return self.__order

    @property
    def geometry(self):
        """A tuple of BFGeometries for BoundingBox faces."""
        def __getBFGeometry(name, attr):
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

    @property
    def grading(self):
        """A simpleGrading (default: simpleGrading(1, 1, 1))."""
        return self.__grading

    @grading.setter
    def grading(self, g):
        self.__grading = g if g else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simpleGrading.'.format(g)

    def make2d(self, planeOrigin, planeNormal, width=0.1):
        """Create a new 2D blockMeshDict from this blockMeshDict.

        Args:
            planeOrigin: Plane origin as (x, y, z).
            planeNormal: Plane normal as (x, y, z).
            width: width of 2d blockMeshDict (default: 01).
        """
        # duplicate blockMeshDict
        bmd = self.duplicate()
        n = vectormath.normalize(planeNormal)

        # project all vertices to plane and move them in direction of normal
        # by half of width
        bmd.__vertices = tuple(
            self.__calculate2dPoints(v, planeOrigin, n, width)
            for v in bmd.vertices)

        # set boundary condition to empty
        # and number of divisions to 1 in shortest side
        minimum = min(bmd.width, bmd.length, bmd.height)
        if bmd.width == minimum:
            bmd.nDivXYZ = (1, bmd.nDivXYZ[1], bmd.nDivXYZ[2])
            # set both sides to empty

        elif bmd.length == minimum:
            bmd.nDivXYZ = (bmd.nDivXYZ[0], 1, bmd.nDivXYZ[2])
            # set inlet and outlet to empty
            # bmd.inlet.boundaryCondition = Empty()

        elif bmd.height == minimum:
            bmd.nDivXYZ = (bmd.nDivXYZ[0], bmd.nDivXYZ[1], 1)
            # set top and bottom to empty

        print('WARNING: make2d doesn\'t update boundary conditions to Empty.')
        return bmd

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

    def __updateBoundaryFromSortedVertices(self):
        """Update boundary dictionary based on BFBlockGeometries input."""
        self.values['boundary']['boundingbox'] = {
            'type': 'wall',
            'faces': ((0, 3, 2, 1), (4, 5, 6, 7),
                      (0, 1, 5, 4), (1, 2, 6, 5),
                      (2, 3, 7, 6), (3, 0, 4, 7),
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

        return _x * self.convertToMeters / len(self.__rawvertices), \
            _y * self.convertToMeters / len(self.__rawvertices), \
            _z * self.convertToMeters / len(self.__rawvertices)

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

        sortedPoints = tuple((pt[0], pt[1], z) for z in zValues
                             for pt in sortedPoints2d)
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
