# coding=utf-8
"""OpemFOAM Case for Dynamo."""
import butterfly.case
from .utilities import loadOFMesh, loadOFPoints


class Case(butterfly.case.Case):
    """Butterfly case for Dynamo."""

    def loadMesh(self, innerMesh=True):
        """Return OpenFOAM mesh as a Rhino mesh."""
        if hasattr(self, 'blockMeshDict'):
            convertToMeters = self.blockMeshDict.convertToMeters
        else:
            convertToMeters = 1

        return loadOFMesh(self.polyMeshFolder, convertToMeters, innerMesh)

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        if hasattr(self, 'blockMeshDict'):
            convertToMeters = self.blockMeshDict.convertToMeters
        else:
            convertToMeters = 1

        return loadOFPoints(self.polyMeshFolder, convertToMeters)
