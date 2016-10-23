# coding=utf-8
"""BlockMeshDict class."""
from .foamfile import FoamFile
from .vectormath import angleAnitclockwise
from .grading import SimpleGrading, Grading, MultiGrading
from .parser import CppDictParser
from .geometry import BFGeometry
from math import sqrt
from collections import OrderedDict


class BlockMeshDict(FoamFile):
    """BlockMeshDict.

    Args:
        BFBlockGeometries: A collection of boundary surfaces for bounding box.
        convertToMeters: Scaling factor for the vertex coordinates.
        nDivXYZ: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
        grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
        xAxis: An optional tuple that indicates the xAxis direction
            (default: (1, 0)).
    """

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
    def fromBFGeometries(cls, BFBlockGeometries, convertToMeters=1,
                         nDivXYZ=None, grading=None, xAxis=None):
        """Init BlockMeshDict."""
        # follow snappyHexMeshDict!
        _cls = cls()
        _cls.values['convertToMeters'] = convertToMeters
        _cls.__BFBlockGeometries = BFBlockGeometries

        try:
            # collect uniqe vertices from all BFGeometries
            _cls.__rawvertices = tuple(
                set(v for f in cls.__BFBlockGeometries
                    for vgroup in f.borderVertices
                    for v in vgroup))
        except AttributeError as e:
            raise TypeError('At least one of the input geometries is not a '
                            'Butterfly block geometry:\n{}'.format(e))

        # sort vertices
        _cls.xAxis = xAxis[:2] if xAxis else (1, 0)
        _cls.__vertices = _cls.__sortVertices()

        # update self.values['boundary']
        _cls.__updateBoundaryFromBFBlockGeometries()

        _cls.__order = tuple(range(7))

        _cls.nDivXYZ = nDivXYZ

        # assign grading
        _cls.grading = grading

        return _cls

    def __updateBoundaryFromBFBlockGeometries(self):
        for geo in self.__BFBlockGeometries:
            try:
                self.values['boundary'][geo.name] = {
                    'type': geo.boundaryCondition.type,
                    'faces': (tuple(self.vertices.index(v) for v in verGroup)
                              for verGroup in self.borderVertices)
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

    def BFBlockGeometries(self):
        """Get list of input BFBlockGeometries."""
        return self.__BFBlockGeometries

    @property
    def geometry(self):
        """A tuple of BFGeometries for BoundingBox faces."""
        def __getBFGeometry(name, attr):
            ind = attr['faces'] if hasattr(attr['faces'][0], '__iter__') else \
                (attr['faces'],)

            # unique indecies
            uniuqe = tuple(set(i for inx in ind for i in inx))

            renumberedIndx = tuple(tuple(uniuqe.index(i) for i in inx)
                                   for inx in ind)

            return BFGeometry(name, tuple(self.vertices[i] for i in uniuqe),
                                    renumberedIndx)

        return tuple(__getBFGeometry(name, attr)
                     for name, attr in self.boundary.iteritems())

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

    def nDivXYZByCellSize(self, cellSizeXYZ):
        """Set number of divisions by cell size."""
        x, y, z = cellSizeXYZ
        self.nDivXYZ = int(round(self.width / x)), int(round(self.length / y)), \
            int(round(self.height / z))

    @staticmethod
    def __distance(v1, v2):
        return sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))

    def __averageVerices(self):
        _x, _y, _z = 0, 0, 0

        for ver in self.vertices:
            _x += ver[0]
            _y += ver[1]
            _z += ver[2]

        return _x * self.__convertToMeters / len(self.vertices), \
            _y * self.__convertToMeters / len(self.vertices), \
            _z * self.__convertToMeters / len(self.vertices)

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
        xAxisReversed = (-self.xAxis[0], self.xAxis[1])
        centerPt = self.center[:2]
        sortedPoints2d = \
            sorted(pointGroups[0],
                   key=lambda x: angleAnitclockwise(xAxisReversed,
                                                    tuple(c1 - c2 for c1, c2
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
