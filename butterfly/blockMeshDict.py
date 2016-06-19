"BlockMeshDict class."
from foamfile import FoamFile
import os

class BlockMeshDict(FoamFile):

    def __init__(self, scale, BFSurfaces, blocks):
        FoamFile.__init__(self, name='blockMeshDict', cls='dictionary')
        self.scale = scale
        self.blocks = blocks
        # collect uniqe vertices from all BFSurfaces
        self.vertices = tuple(set(v for f in BFSurfaces for vgroup in f.borderVertices for v in vgroup))
        self.BFSurfaces = BFSurfaces

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

    def save(self, folder):
        with open(os.path.join(folder, "blockMeshDict"), "wb") as outf:
            outf.write(self.toOpenFoam())
