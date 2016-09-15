"""BlockMeshDict class."""
from foamfile import FoamFile


class BlockMeshDict(FoamFile):
    """BlockMeshDict."""

    def __init__(self, convertToMeters, BFBlockGeometries, blocks):
        """Init BlockMeshDict."""
        FoamFile.__init__(self, name='blockMeshDict', cls='dictionary',
                          location='system')
        self.convertToMeters = convertToMeters
        self.blocks = blocks
        self.BFBlockGeometries = BFBlockGeometries
        try:
            # collect uniqe vertices from all BFSurfaces
            self.vertices = tuple(set(v for f in self.BFBlockGeometries
                                      for vgroup in f.borderVertices
                                      for v in vgroup))
        except AttributeError as e:
            raise TypeError('At least one of the input geometries is not a '
                            'Butterfly block geometry:\n{}'.format(e))

        self.center = self.__averageVerices()

    def __averageVerices(self):
        _x, _y, _z = 0, 0, 0

        for ver in self.vertices:
            _x += ver[0]
            _y += ver[1]
            _z += ver[2]

        return _x / len(self.vertices), \
            _y / len(self.vertices), \
            _z / len(self.vertices)

    def toOpenFOAM(self):
        """Return OpenFOAM representation as a string."""
        _hea = self.header()
        _body = "\nconvertToMeters %.4f;\n" \
                "\n" \
                "vertices\n" \
                "(\n%s\n);\n" \
                "\n" \
                "blocks\n" \
                "(\n%s\n);\n" \
                "\n" \
                "edges\n" \
                "(%s);\n" \
                "\n" \
                "boundary\n" \
                "(%s);\n" \
                "\n" \
                "mergePatchPair\n" \
                "(%s);\n"

        return _hea + \
            _body % (
                self.convertToMeters,
                "\n".join(tuple(str(ver).replace(",", "")
                          for ver in self.vertices)),
                "\n".join(block.toBlockMeshDict(self.vertices)
                          for block in self.blocks),  # blocks
                "\n",  # edges
                "\n".join(srf.toBlockMeshDict(self.vertices)
                          for srf in self.BFBlockGeometries),
                "\n")  # merge patch pair

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """BlockMeshDict representation."""
        return "Butterfly::%s" % self.__class__.__name__
