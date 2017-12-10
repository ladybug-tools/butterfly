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

    __default_values = OrderedDict()
    __default_values['convertToMeters'] = 1
    __default_values['vertices'] = None
    __default_values['blocks'] = None
    __default_values['boundary'] = {}

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='blockMeshDict', cls='dictionary',
                          location='system', default_values=self.__default_values,
                          values=values)

        self._bf_block_geometries = None  # this will be overwritten in classmethods
        self._vertices = []
        self._is_from_vertices = False
        self._x_axis = None
        # variables for 2d blockMeshDict
        self._is_2d_in_x_dir = False
        self._is_2d_in_y_dir = False
        self._is_2d_in_z_dir = False
        self._original_3d_vertices = None
        self._order = []
        self.n_div_xyz = None
        self.grading = None

    @classmethod
    def from_file(cls, filepah, convertToMeters=1):
        """Create a blockMeshDict from file.

        Args:
            filepah: Full path to blockMeshDict.
            converToMeters: converToMeters for the new document. This values
                will be used to update the vertices to the new units. Default
                is 1 which means blockMeshDict will be converted to meters.
        """
        _cls = cls()

        with open(filepah, 'rb') as bf:
            lines = CppDictParser.remove_comments(bf.read())
            bmd = ' '.join(lines.replace('\r\n', ' ').replace('\n', ' ').split())

        _cls.values['convertToMeters'] = convertToMeters

        original_convertToMeters = float(
            bmd.split('convertToMeters')[-1].split(';')[0])

        conversion = convertToMeters / original_convertToMeters

        # find vertices
        vertices = list(eval(','.join(bmd.split('vertices')[-1]
                                      .split(';')[0]
                                      .strip()[1:-1]
                                      .split())))

        _cls._vertices = list(tuple(i / conversion for i in v)
                              for v in vertices)

        # get blocks, order of vertices, n_div_xyz, grading
        blocks = bmd.split('blocks')[-1].split(';')[0].strip()
        xyz, simpleGrading = blocks.split('simpleGrading')

        _cls._order, _cls.n_div_xyz = eval(','.join(xyz.split('hex')[-1].split()))

        simpleGrading = eval(','.join(simpleGrading.strip()[:-1]
                                      .replace('( ', '(')
                                      .replace(' )', ')')
                                      .split()))

        _cls.grading = SimpleGrading(
            *(MultiGrading(tuple(Grading(*i) for i in g))
              if isinstance(g, tuple) else Grading(g)
              for g in simpleGrading))

        # recreate boundary faces
        boundary_string = bmd.replace(' (', '(').replace(' )', ')') \
            .split('boundary(')[-1].strip().replace('});', '}') \
            .replace('));', ');').replace('((', ' (').replace(')(', ') (')

        _cls.values['boundary'] = {}
        for key, values in CppDictParser(boundary_string).values.iteritems():
            if isinstance(values, dict) and 'type' in values and 'faces' in values:
                values['faces'] = eval(str(values['faces']).replace(' ', ','))

                _cls.values['boundary'][key] = values

        del((lines, bmd))
        return _cls

    @classmethod
    def from_origin_and_size(cls, origin, width, length, height, convertToMeters=1,
                             n_div_xyz=None, grading=None, x_axis=None):
        """Create BlockMeshDict from bf_block_geometries.

        Args:
            origin: Minimum point of bounding box as (x, y, z).
            width: Width in x direction.
            length: Length in y direction.
            height: Height in y direction.
            convertToMeters: Scaling factor for the vertex coordinates.
            n_div_xyz: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            x_axis: An optional tuple that indicates the x_axis direction
                (default: (1, 0)).
        """
        _x_axis = vectormath.normalize(
            (x_axis[0], x_axis[1], 0) if x_axis else (1, 0, 0))
        _z_axis = (0, 0, 1)
        _y_axis = vectormath.cross_product(_z_axis, _x_axis)
        vertices = [
            vectormath.move(origin,
                            vectormath.sums((vectormath.scale(_x_axis, i * width),
                                             vectormath.scale(_y_axis, j * length),
                                             vectormath.scale(_z_axis, k * height))
                                            ))
            for i in range(2) for j in range(2) for k in range(2)]

        return cls.from_vertices(vertices, convertToMeters, n_div_xyz, grading,
                                 x_axis)

    @classmethod
    def from_min_max(cls, min_pt, max_pt, convertToMeters=1, n_div_xyz=None,
                     grading=None, x_axis=None):
        """Create BlockMeshDict from minimum and maximum point.

        Args:
            min_pt: Minimum point of bounding box as (x, y, z).
            max_pt: Maximum point of bounding box as (x, y, z).
            convertToMeters: Scaling factor for the vertex coordinates.
            n_div_xyz: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            x_axis: An optional tuple that indicates the x_axis direction
                (default: (1, 0)).
        """
        _x_axis = vectormath.normalize(
            (x_axis[0], x_axis[1], 0) if x_axis else (1, 0, 0))
        _z_axis = (0, 0, 1)
        _y_axis = vectormath.cross_product(_z_axis, _x_axis)
        diagonal2_d = tuple(i - j for i, j in zip(max_pt, min_pt))[:2]
        _angle = radians(vectormath.angle_anitclockwise(_x_axis[:2], diagonal2_d))
        width = cos(_angle) * vectormath.length(diagonal2_d)
        length = sin(_angle) * vectormath.length(diagonal2_d)
        height = max_pt[2] - min_pt[2]

        vertices = [
            vectormath.move(min_pt,
                            vectormath.sums((vectormath.scale(_x_axis, i * width),
                                             vectormath.scale(_y_axis, j * length),
                                             vectormath.scale(_z_axis, k * height))
                                            ))

            for i in range(2) for j in range(2) for k in range(2)]

        return cls.from_vertices(vertices, convertToMeters, n_div_xyz, grading,
                                 x_axis)

    @classmethod
    def from_vertices(cls, vertices, convertToMeters=1, n_div_xyz=None,
                      grading=None, x_axis=None):
        """Create BlockMeshDict from vertices.

        Args:
            vertices: 8 vertices to define the bounding box.
            convertToMeters: Scaling factor for the vertex coordinates.
            n_div_xyz: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            x_axis: An optional tuple that indicates the x_axis direction
                (default: (1, 0)).
        """
        _cls = cls()
        _cls.values['convertToMeters'] = convertToMeters
        _cls._rawvertices = vertices

        # sort vertices
        _cls.x_axis = x_axis

        _cls._vertices = _cls._sort_vertices()

        _cls._order = tuple(range(8))

        # update self.values['boundary']
        _cls._update_boundary_from_sorted_vertices()

        _cls.n_div_xyz = n_div_xyz

        # assign grading
        _cls.grading = grading
        _cls._is_from_vertices = True
        return _cls

    @classmethod
    def from_bf_block_geometries(cls, bf_block_geometries, convertToMeters=1,
                                 n_div_xyz=None, grading=None, x_axis=None):
        """Create BlockMeshDict from bf_block_geometries.

        Args:
            bf_block_geometries: A collection of boundary surfaces for bounding box.
            convertToMeters: Scaling factor for the vertex coordinates.
            n_div_xyz: Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5).
            grading: A simpleGrading (default: simpleGrading(1, 1, 1)).
            x_axis: An optional tuple that indicates the x_axis direction
                (default: (1, 0)).
        """
        _cls = cls()
        _cls.values['convertToMeters'] = convertToMeters
        _cls._bf_block_geometries = bf_block_geometries

        try:
            # collect uniqe vertices from all bf_geometries
            _cls._rawvertices = tuple(
                set(v for f in _cls._bf_block_geometries
                    for vgroup in f.border_vertices
                    for v in vgroup))
        except AttributeError as e:
            raise TypeError('At least one of the input geometries is not a '
                            'Butterfly block geometry:\n\t{}'.format(e))

        # sort vertices
        _cls.x_axis = x_axis[:2] if x_axis else (1, 0)
        _cls._vertices = _cls._sort_vertices()

        # update self.values['boundary']
        _cls.__update_boundary_from_bf_block_geometries()

        _cls._order = tuple(range(8))

        _cls.n_div_xyz = n_div_xyz

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
    def is2d_in_x_direction(self):
        """Return True if the case is 2d in X direction."""
        return self._is_2d_in_x_dir

    @property
    def is2d_in_y_direction(self):
        """Return True if the case is 2d in Y direction."""
        return self._is_2d_in_y_dir

    @property
    def is2d_in_z_direction(self):
        """Return True if the case is 2d in Z direction."""
        return self._is_2d_in_z_dir

    @property
    def vertices(self):
        """Get the sorted list of vertices."""
        return self._vertices

    @property
    def x_axis(self):
        """X axis as a tuple."""
        if self._x_axis:
            return self._x_axis
        else:
            self._x_axis = vectormath.normalize(
                vectormath.subtract(self.vertices[1], self.vertices[0])
            )
        return self._x_axis

    @x_axis.setter
    def x_axis(self, v):
        """X axis."""
        v = v or (1, 0, 0)
        self._x_axis = vectormath.normalize((v[0], v[1], 0))

    @property
    def y_axis(self):
        """Y axis."""
        return vectormath.cross_product(self.z_axis, self.x_axis)

    @property
    def z_axis(self):
        """Z axis."""
        return (0, 0, 1)

    def update_vertices(self, vertices, x_axis=None):
        """Update blockMeshDict vertices."""
        self._rawvertices = vertices

        # sort vertices
        if x_axis:
            self.x_axis = x_axis

        self._vertices = self._sort_vertices()

        self._order = tuple(range(8))

        # update self.values['boundary']
        self._update_boundary_from_sorted_vertices()

    @property
    def vertices_order(self):
        """Get order of vertices in blocks."""
        return self._order

    @property
    def geometry(self):
        """A tuple of bf_geometries for BoundingBox faces."""
        def _get_bf_geometry(name, attr):
            if name == 'boundingbox_empty':
                bc = EmptyBoundaryCondition()
            else:
                bc = BoundingBoxBoundaryCondition()

            ind = attr['faces'] if hasattr(attr['faces'][0], '__iter__') else \
                (attr['faces'],)

            # unique indecies
            uniuqe = tuple(set(i for inx in ind for i in inx))

            renumbered_indx = tuple(tuple(uniuqe.index(i) for i in inx)
                                    for inx in ind)

            return BFGeometry(name, tuple(self.vertices[i] for i in uniuqe),
                              renumbered_indx, boundary_condition=bc)

        if not self._bf_block_geometries:
            self._bf_block_geometries = tuple(
                _get_bf_geometry(name, attr)
                for name, attr in self.boundary.iteritems())

        return self._bf_block_geometries

    @property
    def width(self):
        """Length of block in X direction."""
        return self._distance(self.vertices[self.vertices_order[0]],
                              self.vertices[self.vertices_order[1]])

    @property
    def length(self):
        """Length of block in Y direction."""
        return self._distance(self.vertices[self.vertices_order[0]],
                              self.vertices[self.vertices_order[3]])

    @property
    def height(self):
        """Length of block in Z direction."""
        return self._distance(self.vertices[self.vertices_order[0]],
                              self.vertices[self.vertices_order[4]])

    @property
    def center(self):
        """Get center of the block."""
        return self._average_verices()

    @property
    def min_pt(self):
        """Return minimum pt x, y, z in this block."""
        return self.vertices[self.vertices_order[0]]

    @property
    def max_pt(self):
        """Return maximum pt x, y, z in this block."""
        return self.vertices[self.vertices_order[6]]

    @property
    def min_z(self):
        """Return minimum Z value of vertices in this block."""
        return self.vertices[self.vertices_order[0]][2]

    @property
    def n_div_xyz(self):
        """Number of divisions in (x, y, z) as a tuple (default: 5, 5, 5)."""
        return self._n_div_xyz

    @n_div_xyz.setter
    def n_div_xyz(self, d_xyz):
        self._n_div_xyz = tuple(int(v) for v in d_xyz) if d_xyz else (5, 5, 5)
        if self._is_2d_in_x_dir:
            self._n_div_xyz = 1, self._n_div_xyz[1], self._n_div_xyz[2]
        elif self._is_2d_in_y_dir:
            self._n_div_xyz = self._n_div_xyz[0], 1, self._n_div_xyz[2]
        elif self._is_2d_in_z_dir:
            self._n_div_xyz = self._n_div_xyz[0], self._n_div_xyz[1], 1

    @property
    def grading(self):
        """A simpleGrading (default: simpleGrading(1, 1, 1))."""
        return self._grading

    @grading.setter
    def grading(self, g):
        self._grading = g if g else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simpleGrading.'.format(g)

    def make3d(self):
        """Reload the 3d blockMeshDict if it has been converted to 2d."""
        if not self._original_3d_vertices:
            print('This blockMeshDict is already a 3d blockMeshDict.')
            return
        self._vertices = self._original_3d_vertices
        self._is_2d_in_x_dir = False
        self._is_2d_in_y_dir = False
        self._is_2d_in_z_dir = False

    def make2d(self, plane_origin, plane_normal, width=0.1):
        """Make the blockMeshDict two dimensional.

        Args:
            plane_origin: Plane origin as (x, y, z).
            plane_normal: Plane normal as (x, y, z).
            width: width of 2d blockMeshDict (default: 01).
        """
        # copy original vertices
        if not self._original_3d_vertices:
            self._original_3d_vertices = self.vertices
        else:
            # load original 3d vertices
            self.make3d()

        n = vectormath.normalize(plane_normal)

        # project all vertices to plane and move them in direction of normal
        # by half of width
        self._vertices = [
            self._calculate2d_points(v, plane_origin, n, width)
            for v in self.vertices]

        # set boundary condition to empty
        # and number of divisions to 1 in shortest side
        minimum = min(self.width, self.length, self.height)
        if self.width == minimum:
            self.n_div_xyz = (1, self.n_div_xyz[1], self.n_div_xyz[2])
            self._is_2d_in_x_dir = True
            # set both sides to empty
            self._set_boundary_to_empty(4)
            self._set_boundary_to_empty(5)

        elif self.length == minimum:
            self.n_div_xyz = (self.n_div_xyz[0], 1, self.n_div_xyz[2])
            self._is_2d_in_y_dir = True
            # set inlet and outlet to empty
            self._set_boundary_to_empty(0)
            self._set_boundary_to_empty(1)

        elif self.height == minimum:
            self.n_div_xyz = (self.n_div_xyz[0], self.n_div_xyz[1], 1)
            self._is_2d_in_z_dir = True
            # set top and bottom to empty
            self._set_boundary_to_empty(2)
            self._set_boundary_to_empty(3)

    def expand_uniform_by_cells_count(self, count, renumber_division=True):
        """Expand blockMeshDict boundingbox for n cells from all sides.

        This method will increase the number of divisions by 2 to keep the size
        of the cells unchanged unless renumber_division is set to False. Use a
        negative count to shrink the bounding box.
        """
        x, y, z = self.n_div_xyz
        self.expand_x((self.width / float(x)) * count)
        self.expand_y((self.length / float(y)) * count)
        self.expand_z((self.height / float(z)) * count)
        if renumber_division:
            self.n_div_xyz = (x + 2 * count, y + 2 * count, z + 2 * count)

    def expand_by_cells_count(self, x_count, y_count, z_count, renumber_division=True):
        """Expand blockMeshDict boundingbox for n cells from all sides.

        This method will increase the number of divisions by 2 to keep the size
        of the cells unchanged unless renumber_division is set to False. Use a
        negative count to shrink the bounding box.
        """
        x, y, z = self.n_div_xyz
        self.expand_x((self.width / float(x)) * x_count)
        self.expand_y((self.length / float(y)) * y_count)
        self.expand_z((self.height / float(z)) * z_count)
        if renumber_division:
            self.n_div_xyz = (x + 2 * x_count, y + 2 * y_count, z + 2 * z_count)

    def expand_uniform(self, dist):
        """Expand blockMeshDict boundingbox for dist in all directions."""
        if not dist:
            return
        self.expand_x(dist)
        self.expand_y(dist)
        self.expand_z(dist)

    def expand_x(self, dist):
        """Expand blockMeshDict boundingbox for dist in x and -x directions."""
        _x_axis = self.x_axis

        for i in (0, 3, 7, 4):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_x_axis, -dist))

        for i in (1, 2, 6, 5):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_x_axis, dist))

    def expand_y(self, dist):
        """Expand blockMeshDict boundingbox for dist in y and -y directions."""
        _y_axis = self.y_axis
        for i in (0, 1, 5, 4):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_y_axis, -dist))

        for i in (3, 2, 6, 7):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_y_axis, dist))

    def expand_z(self, dist):
        """Expand blockMeshDict boundingbox for dist in z and -z directions."""
        _z_axis = (0, 0, 1)
        for i in (0, 1, 2, 3):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_z_axis, -dist))

        for i in (4, 5, 6, 7):
            self.vertices[i] = vectormath.move(
                self.vertices[i], vectormath.scale(_z_axis, dist))

    @staticmethod
    def _calculate2d_points(v, o, n, w):
        # project point
        p = vectormath.project(v, o, n)
        # move the projected point backwards for half of the width
        t = vectormath.scale(vectormath.normalize(vectormath.subtract(v, p)),
                             w / 2.0)
        return vectormath.move(p, t)

    def n_div_xyz_by_cell_size(self, cell_size_xyz):
        """Set number of divisions by cell size."""
        x, y, z = cell_size_xyz
        self.n_div_xyz = int(round(self.width / x)), int(round(self.length / y)), \
            int(round(self.height / z))

    def update_meshing_parameters(self, meshing_parameters):
        """Update meshing parameters for blockMeshDict."""
        if not meshing_parameters:
            return

        assert hasattr(meshing_parameters, 'isMeshingParameters'), \
            'Expected MeshingParameters not {}'.format(type(meshing_parameters))

        if meshing_parameters.cell_size_xyz:
            self.n_div_xyz_by_cell_size(meshing_parameters.cell_size_xyz)

        if meshing_parameters.grading:
            self.grading = meshing_parameters.grading

    @property
    def bottom_face_indices(self):
        """Get indecies for bottom face."""
        return (self.vertices_order[0], self.vertices_order[3],
                self.vertices_order[2], self.vertices_order[1])

    @property
    def top_face_indices(self):
        """Get indecies for top face."""
        return (self.vertices_order[4], self.vertices_order[5],
                self.vertices_order[6], self.vertices_order[7])

    @property
    def right_face_indices(self):
        """Get indecies for right face."""
        return (self.vertices_order[1], self.vertices_order[2],
                self.vertices_order[6], self.vertices_order[5])

    @property
    def left_face_indices(self):
        """Get indecies for left face."""
        return (self.vertices_order[3], self.vertices_order[0],
                self.vertices_order[4], self.vertices_order[7])

    @property
    def front_face_indices(self):
        """Get indecies for front face."""
        return (self.vertices_order[0], self.vertices_order[1],
                self.vertices_order[5], self.vertices_order[4])

    @property
    def back_face_indices(self):
        """Get indecies for back face."""
        return (self.vertices_order[2], self.vertices_order[3],
                self.vertices_order[7], self.vertices_order[6])

    def get_face_indices(self, face_index):
        """Update boundary to empty for one of the faces.

        Args:
            face_index: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        face_indices = {0: self.front_face_indices, 1: self.back_face_indices,
                        2: self.bottom_face_indices, 3: self.top_face_indices,
                        4: self.right_face_indices, 5: self.left_face_indices}

        return face_indices[face_index]

    @property
    def bottom_face_vertices(self):
        """Get vertices for bottom face."""
        return tuple(self.vertices[o] for o in self.bottom_face_indices)

    @property
    def top_face_vertices(self):
        """Get vertices for top face."""
        return tuple(self.vertices[o] for o in self.top_face_indices)

    @property
    def right_face_vertices(self):
        """Get vertices for right face."""
        return tuple(self.vertices[o] for o in self.right_face_indices)

    @property
    def left_face_vertices(self):
        """Get vertices for left face."""
        return tuple(self.vertices[o] for o in self.left_face_indices)

    @property
    def front_face_vertices(self):
        """Get vertices for front face."""
        return tuple(self.vertices[o] for o in self.front_face_indices)

    @property
    def back_face_vertices(self):
        """Get vertices for back face."""
        return tuple(self.vertices[o] for o in self.back_face_indices)

    def get_face_vertices(self, face_index):
        """Update boundary to empty for one of the faces.

        Args:
            face_index: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        face_vertices = {0: self.front_face_vertices, 1: self.back_face_vertices,
                         2: self.bottom_face_vertices, 3: self.top_face_vertices,
                         4: self.right_face_vertices, 5: self.left_face_vertices}

        return face_vertices[face_index]

    def _set_boundary_to_empty(self, face_index):
        """Update boundary to empty for the face based on index.

        Args:
            face_index: 0 - front, 1 - back, 2 - bottom, 3 - top, 4 - right,
                5 - left.
        """
        # get indices and vertices for the face_index
        ind = self.get_face_indices(face_index)

        if self._is_from_vertices:
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

                    for geo in self._bf_block_geometries:
                        if geo.name == name:
                            geo.boundary_condition = EmptyBoundaryCondition()
                    break

    def _update_boundary_from_sorted_vertices(self):
        """Update boundary dictionary based ordered vertices."""
        self.values['boundary']['boundingbox'] = {
            'type': 'wall',
            'faces': (self.bottom_face_indices, self.top_face_indices,
                      self.right_face_indices, self.left_face_indices,
                      self.front_face_indices, self.back_face_indices,
                      )
        }

    def __update_boundary_from_bf_block_geometries(self):
        """Update boundary dictionary based on bf_block_geometries input."""
        for geo in self._bf_block_geometries:
            try:
                self.values['boundary'][geo.name] = {
                    'type': geo.boundary_condition.type,
                    'faces': tuple(tuple(self.vertices.index(v) for v in verGroup)
                                   for verGroup in geo.border_vertices)
                }
            except AttributeError as e:
                raise TypeError('Wrong input geometry!\n{}'.format(e))

    def __boundary_to_openfoam(self):
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
    def _distance(v1, v2):
        return sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))

    def _average_verices(self):
        _x, _y, _z = 0, 0, 0

        for ver in self._rawvertices:
            _x += ver[0]
            _y += ver[1]
            _z += ver[2]

        numofver = len(self._rawvertices)
        return _x / numofver, _y / numofver, _z / numofver

    def _sort_vertices(self):
        """sort input vertices."""
        groups = {}
        for p in self._rawvertices:
            if p[2] not in groups:
                groups[p[2]] = []

            groups[p[2]].append((p[0], p[1]))

        z_values = sorted(groups.keys())
        point_groups = groups.values()

        assert len(z_values) == 2, \
            'Number of Z values must be 2 not {}: {}.'.format(len(z_values),
                                                              z_values)

        for g in point_groups:
            assert len(g) == 4

        # the points in both height are identical so I just take the first group
        # and sort them
        x_axis_reversed = (-self.x_axis[0], -self.x_axis[1])
        center_pt = self.center[:2]
        sorted_points2d = \
            sorted(point_groups[0],
                   key=lambda x: vectormath.angle_anitclockwise(
                       x_axis_reversed, tuple(c1 - c2 for c1, c2
                                              in zip(x, center_pt))))

        sorted_points = [(pt[0], pt[1], z) for z in z_values for pt in sorted_points2d]
        return sorted_points

    def to_openfoam(self):
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
                str(self.vertices_order).replace(",", ""),
                str(self.n_div_xyz).replace(",", ""),
                self.grading,  # blocks
                "\n",  # edges
                self.__boundary_to_openfoam(),  # boundary
                "\n")  # merge patch pair

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """BlockMeshDict representation."""
        return self.to_openfoam()
