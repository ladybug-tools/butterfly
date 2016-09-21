"""OpemFOAM Case for Grasshopper."""
import os

from ..core import OpemFOAMCase
from .postprocess import loadOFMeshToRhino, loadOFPointsToRhino


class Case(OpemFOAMCase):
    """Butterfly case for Grasshopper."""

    def loadMesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFMeshToRhino(os.path.join(self.constantDir, "polyMesh"))

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFPointsToRhino(os.path.join(self.constantDir, "polyMesh"))
