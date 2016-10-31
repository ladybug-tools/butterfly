# coding=utf-8
"""RefinementRegion for Grasshopper."""
from butterfly.refinementRegion import RefinementRegion
from .geometry import MeshGH


class RefinementRegionGH(RefinementRegion):
    """Butterfly refinement region in Grasshopper.

    Attributes:
        name: Name as a string (A-Z a-z 0-9).
        geometries: A list of Grasshopper meshes or Breps. All input geometries
            will be converted as a joined mesh.
        refinementMode: Refinement mode (0: inside, 1: outside, 2: distance)
        meshingParameters: Grasshopper meshing parameters for meshing brep geometries.
            In case geometry is Mesh this input won't be used.
    """

    def __init__(self, name, geometries, refinementMode, meshingParameters=None):
        """Init Butterfly geometry."""
        _mesh = MeshGH(geometries, meshingParameters)
        self.__geometry = _mesh.geometry
        RefinementRegion.__init__(self, name, _mesh.vertices, _mesh.faceIndices,
                                  _mesh.normals, refinementMode)
