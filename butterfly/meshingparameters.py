# coding=utf-8
"""Butterfly Meshing Parameters.

Collection of meshing parameters for blockMesh and snappyHexMesh.
"""
from .grading import SimpleGrading
from copy import deepcopy


class MeshingParameters(object):
    """Meshing parameters.

    Attributes:
        cell_size_xyz: Cell size in (x, y, z) as a tuple (default: length / 5).
            This value updates number of divisions in blockMeshDict.
        grading: A simple_grading (default: simple_grading(1, 1, 1)). This value
            updates grading in blockMeshDict.
        location_in_mesh: A tuple for the location of the mesh to be kept. This
            value updates location_in_mesh in snappyHexMeshDict.
        glob_refine_level: A tuple of (min, max) values for global refinment. This
            value updates globalRefinementLevel in snappyHexMeshDict.
    """

    def __init__(self, cell_size_xyz=None, grading=None, location_in_mesh=None,
                 glob_refine_level=None):
        """Init meshing parameters."""
        # blockMeshDict
        try:
            self.cell_size_xyz = None if not cell_size_xyz else tuple(cell_size_xyz)
        except TypeError:
            # Point in Dynamo is not iterable
            self.cell_size_xyz = (cell_size_xyz.X, cell_size_xyz.Y, cell_size_xyz.Z)

        self.grading = grading  # blockMeshDict
        # snappyHexMeshDict
        try:
            self.location_in_mesh = None if not location_in_mesh else tuple(
                location_in_mesh)
        except TypeError:
            # Point in Dynamo is not iterable
            self.location_in_mesh = (
                location_in_mesh.X,
                location_in_mesh.Y,
                location_in_mesh.Z)

        # snappyHexMeshDict
        self.glob_refine_level = None if not glob_refine_level else tuple(
            glob_refine_level)

    @property
    def is_meshing_parameters(self):
        """Return True."""
        return True

    @property
    def grading(self):
        """A simple_grading (default: simple_grading(1, 1, 1))."""
        return self.__grading

    @grading.setter
    def grading(self, g):
        self.__grading = g if g else SimpleGrading()

        assert hasattr(self.grading, 'isSimpleGrading'), \
            'grading input ({}) is not a valid simple_grading.'.format(g)

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
                       for i in (self.cell_size_xyz, self.grading) if i))
        )
