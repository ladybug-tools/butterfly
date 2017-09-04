import math


class Solid(object):
    """A solid object; the root element of an STL file."""

    #: The name given to the object by the STL file header.
    name = None

    #: :py:class:`list` of :py:class:`stl.Facet` objects representing the
    #: facets (triangles) that make up the exterior surface of this object.
    facets = []

    def __init__(self, name=None, facets=None):
        self.name = name
        self.facets = facets if facets is not None else []

    def add_facet(self, *args, **kwargs):
        """Append a new facet to the object.

        Takes the same arguments as the :py:class:`stl.Facet` type.
        """
        self.facets.append(Facet(*args, **kwargs))

    @property
    def normals(self):
        """Get facet normals."""
        return tuple(facet.normal for facet in self.facets)

    @property
    def surface_area(self):
        """The sum of the areas of all facets in the object."""
        return reduce(
            lambda accum, facet: accum + facet.area,
            self.facets,
            0.0,
        )

    @property
    def vertices(self):
        """Unique vertices for all facets."""
        return tuple(set(ver for facet in self.facets for ver in facet.vertices))

    def write_binary(self, file):
        """Write this object to a file in STL *binary* format.

        ``file`` must be a file-like object (supporting a ``write`` method),
        to which the data will be written.
        """
        from stl.binary import write
        write(self, file)

    def write_ascii(self, file):
        """Write this object to a file in STL *ascii* format.

        ``file`` must be a file-like object (supporting a ``write`` method),
        to which the data will be written.
        """
        from stl.ascii import write
        write(self, file)

    def __eq__(self, other):
        if isinstance(other, Solid):
            if self.name != other.name:
                return False
            if len(self.facets) != len(other.facets):
                return False
            for i, self_facet in enumerate(self.facets):
                if self_facet != other.facets[i]:
                    return False
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<stl.types.Solid name=%r, facets=%r>' % (
            self.name,
            self.facets,
        )


class Facet(object):
    """A facet (triangle) from a :py:class:`stl.Solid`."""

    #: Raw binary attribute bytes. According to the STL spec these are unused
    #: and thus this should always be empty, but some modeling software
    #: encodes non-standard data in here which callers may wish to access.
    #:
    #: At present these attribute bytes are populated only when reading binary
    #: STL files (since ASCII STL files have no place for this data) *and*
    #: they are ignored when *writing* a binary STL file, so round-tripping
    #: a file through this library will lose the non-standard attribute data.
    attributes = None

    #: The 'normal' vector of the facet, as a :py:class:`stl.Vector3d`.
    normal = None

    #: 3-element sequence of :py:class:`stl.Vector3d` representing the
    #: facet's three vertices, in order.
    vertices = None

    def __init__(self, normal, vertices, attributes=None):
        self.normal = Vector3d(*normal)
        self.vertices = tuple(
            Vector3d(*x) for x in vertices
        )

        if len(self.vertices) != 3:
            raise ValueError('Must pass exactly three vertices')

    def __eq__(self, other):
        if isinstance(other, Facet):
            return (
                self.normal == other.normal and
                self.vertices == other.vertices
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<stl.types.Facet normal=%r, vertices=%r, area=%r>' % (
            self.normal,
            self.vertices,
            self.area,
        )

    @property
    def a(self):
        """The length the side of the facet between vertices[0] and vertices[1]."""
        return abs(
            math.sqrt(
                pow((self.vertices[0].x - self.vertices[1].x), 2) +
                pow((self.vertices[0].y - self.vertices[1].y), 2) +
                pow((self.vertices[0].z - self.vertices[1].z), 2)
            )
        )

    @property
    def b(self):
        """The length of the side of the facet between vertices[0] and vertices[2]."""
        return abs(
            math.sqrt(
                pow((self.vertices[0].x - self.vertices[2].x), 2) +
                pow((self.vertices[0].y - self.vertices[2].y), 2) +
                pow((self.vertices[0].z - self.vertices[2].z), 2)
            )
        )

    @property
    def c(self):
        """The length of the side of the facet between vertices[1] and vertices[2]."""
        return abs(
            math.sqrt(
                pow((self.vertices[1].x - self.vertices[2].x), 2) +
                pow((self.vertices[1].y - self.vertices[2].y), 2) +
                pow((self.vertices[1].z - self.vertices[2].z), 2)
            )
        )

    @property
    def perimeter(self):
        """The length of the perimeter of the facet."""
        return self.a + self.b + self.c

    @property
    def area(self):
        """The surface area of the facet, as computed by Heron's Formula."""
        p = self.perimeter / 2.0
        return abs(math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c)))


class Vector3d(tuple):
    """Three-dimensional vector.

    Used to represent both normals and vertices of :py:class:`stl.Facet`
    objects.

    This is a subtype of :py:class:`tuple`, so can also be treated like a
    three-element tuple in (``x``, ``y``, ``z``) order.
    """

    def __new__(cls, x, y, z):
        return tuple.__new__(cls, (x, y, z))

    def __init__(self, x, y, z):
        pass

    @property
    def x(self):
        """The X value of the vector.

        which most applications interpret as the left-right axis.
        """
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        """The Y value of the vector.

        which most applications interpret as the in-out axis.
        """
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        """The Z value of the vector.

        which most applications interpret as the up-down axis.
        """
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value
