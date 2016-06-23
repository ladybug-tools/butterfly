"BlockMeshDict class."
from foamfile import FoamFile
import os

class BlockMeshDict(FoamFile):

    def __init__(self, scale, BFSurfaces, blocks):
        FoamFile.__init__(self, name='blockMeshDict', cls='dictionary',
                          location='system')
        self.scale = scale
        self.blocks = blocks
        self.BFSurfaces = BFSurfaces
        # collect uniqe vertices from all BFSurfaces
        self.vertices = tuple(set(v for f in BFSurfaces for vgroup in f.borderVertices for v in vgroup))
        self.center = self.__averageVerices()

    def __averageVerices(self):
        _x, _y, _z = 0 , 0, 0

        for ver in self.vertices:
            _x += ver[0]
            _y += ver[1]
            _z += ver[2]

        return _x / len(self.vertices), \
               _y / len(self.vertices), \
               _z / len(self.vertices)

    def toOpenFoam(self):
        _hea = self.header()
        _body = "\nconvertToMeters 1;\n" \
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
                    "\n".join(tuple(str(ver).replace(",", "")
                              for ver in self.vertices)),
                    "\n".join(block.blockMeshDict(self.vertices)
                              for block in self.blocks), #blocks
                    "\n",  # edges
                    "\n".join(srf.blockMeshDict(self.vertices)
                              for srf in self.BFSurfaces),
                    "\n"  # merge patch pair
               )

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "Butterfly::%s" % self.__class__.__name__
