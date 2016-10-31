# coding=utf-8
"""OpemFOAM Case for Grasshopper."""
import os

import butterfly.case
from .postprocess import loadOFMeshToRhino, loadOFPointsToRhino


class Case(butterfly.case.Case):
    """Butterfly case for Grasshopper."""

    def loadMesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFMeshToRhino(self.polyMeshFolder,
                                 convertToMeters=self.blockMeshDict.convertToMeters)

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        return loadOFPointsToRhino(self.polyMeshFolder,
                                   convertToMeters=self.blockMeshDict.convertToMeters)
