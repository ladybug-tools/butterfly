# coding=utf-8
"""Butterfly Meshing Parameters.

Collection of meshing parameters for blockMesh and snappyHexMesh.
"""
from .grading import SimpleGrading
from copy import deepcopy


class MeshingParameters(object):
    """Meshing parameters.

    Attributes:
        cellSizeXYZ: Cell size in (x, y, z) as a tuple (default: length / 5).
            This value updates number of divisions in blockMeshDict.
        grading: A simpleGrading (default: simpleGrading(1, 1, 1)). This value
            updates grading in blockMeshDict.
        locationInMesh: A tuple for the location of the mesh to be kept. This
            value updates locationInMesh in snappyHexMeshDict.
        globRefineLevel: A tuple of (min, max) values for global refinment. This
            value updates globalRefinementLevel in snappyHexMeshDict.
    """

    def __init__(self, cellSizeXYZ=None, grading=None, locationInMesh=None,
                 globRefineLevel=None):
        """Init meshing parameters."""
        # blockMeshDict
        try:
            self.cellSizeXYZ = None if not cellSizeXYZ else tuple(cellSizeXYZ)
        except TypeError:
            # Point in Dynamo is not iterable
            self.cellSizeXYZ = (cellSizeXYZ.X, cellSizeXYZ.Y, cellSizeXYZ.Z)

        self.grading = grading  # blockMeshDict
        # snappyHexMeshDict
        try:
            self.locationInMesh = None if not locationInMesh else tuple(locationInMesh)
        except TypeError:
            # Point in Dynamo is not iterable
            self.locationInMesh = (locationInMesh.X, locationInMesh.Y, locationInMesh.Z)

        # snappyHexMeshDict
        self.globRefineLevel = None if not globRefineLevel else tuple(globRefineLevel)

    @property
    def isMeshingParameters(self):
        """Return True."""
        return True

    @property
    def grading(self):
        """A simpleGrading (default: simpleGrading(1, 1, 1))."""
        return self.__grading

    @grading.setter
    def grading(self, g):
        self.__grading = g if g else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simpleGrading.'.format(g)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Meshing parameters representation."""
        return "MeshingParameters::{}".format(
            '::'.join((str(i).replace('\n', '').replace('\t', ' ')
                       for i in (self.cellSizeXYZ, self.grading) if i))
        )
