# coding=utf-8
"""OpemFOAM Case for Grasshopper."""
import butterfly.case
from .postprocess import loadOFMeshToRhino, loadOFPointsToRhino


class Case(butterfly.case.Case):
    """Butterfly case for Grasshopper."""

    def loadMesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        if hasattr(self, 'blockMeshDict'):
            convertToMeters = self.blockMeshDict.convertToMeters
        else:
            convertToMeters = 1

        return loadOFMeshToRhino(self.polyMeshFolder, convertToMeters)

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        if hasattr(self, 'blockMeshDict'):
            convertToMeters = self.blockMeshDict.convertToMeters
        else:
            convertToMeters = 1

        return loadOFPointsToRhino(self.polyMeshFolder, convertToMeters)
