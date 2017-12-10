# coding=utf-8
"""Butterfly make2d Parameters.

Parameters to convert a 3d OpenFOAM case to 2d.
"""
from copy import deepcopy


# TODO(): Add check for input values.
class Make2dParameters(object):
    """Make2d parameters.

    Attributes:
        origin: Plane origin as (x, y, z).
        normal: Plane normal as (x, y, z).
        width: width of 2d blockMeshDict (default: 0.5).
    """

    def __init__(self, origin, normal, width=0.5):
        """Init make2d parameters."""
        self.origin = tuple(origin)
        self.normal = tuple(normal)
        self.width = width or 0.5

    @property
    def isMake2dParameters(self):
        """Return True."""
        return True

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Make2d parameters representation."""
        return "Make2dParameters::o({})::n({})".format(
            ','.join('%.3f' % o for o in self.origin),
            ','.join('%.3f' % n for n in self.normal)
        )
