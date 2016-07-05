"""OpemFOAM Case for Grasshopper."""
import os

from ..core import OpemFOAMCase
from .postprocess import loadOFMeshToRhino, loadOFPointsToRhino, loadOFVectorsToRhino


class Case(OpemFOAMCase):
    """Butterfly case for Grasshopper."""

    def loadMesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFMeshToRhino(os.path.join(self.constantDir, "polyMesh"))

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFPointsToRhino(os.path.join(self.constantDir, "polyMesh"))

    def loadVelocity(self, timestep=None):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # find results folders
        _folders = self.getResultsSubfolders()

        # if there is no timestep pick the last one
        _folder = _folders[-1]

        if timestep:
            try:
                # pick the one based on timestep
                _folder = _folders[timestep + 1]
            except IndexError:
                pass

        return loadOFVectorsToRhino(os.path.join(self.projectDir, str(_folder)),
                                    variable='U')
