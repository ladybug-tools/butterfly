# coding=utf-8
"""Butterfly refinement region."""
import sys
from copy import deepcopy
from .geometry import _BFMesh
from .geometry import bf_geometry_from_stl_file


class RefinementRegion(_BFMesh):
    """Butterfly refinement region.

    Attributes:
        name: Name as a string (A-Z a-z 0-9 _).
        vertices: A flatten list of (x, y, z) for vertices.
        face_indices: A flatten list of (a, b, c) for indices for each face.
        normals: A flatten list of (x, y, z) for face normals.
        refinement_mode: Refinement mode (0: inside, 1: outside, 2: distance)
    """

    def __init__(self, name, vertices, face_indices, normals, refinement_mode):
        """Init Butterfly geometry."""
        _BFMesh.__init__(self, name, vertices, face_indices, normals)
        self.refinement_mode = refinement_mode

    @property
    def isRefinementRegion(self):
        """Return True for Butterfly refinement region."""
        return True

    @property
    def refinement_mode(self):
        """Boundary condition."""
        return self.__refinement_mode

    @refinement_mode.setter
    def refinement_mode(self, rm):
        assert hasattr(rm, 'isRefinementMode'), \
            '{} is not a Butterfly refinement mode.'.format(rm)

        self.__refinement_mode = rm


class _RefinementMode(object):
    """Base class for refinement modes.

    Inside, outside, distance

    Attributes:
        levels: A list of (x, y) values for levels.
    """

    def __init__(self, levels):
        self.levels = levels

    @property
    def isRefinementMode(self):
        """Return True for Butterfly refinement mode."""
        return True

    @property
    def levels(self):
        """Set and get levels for refinment region."""
        return self.__levels

    @levels.setter
    def levels(self, lev):
        for l in lev:
            assert len(l) == 2, \
                'Length of each level ({}) should be 2.'.format(len(l))

        # sort levels based on first item for distance
        self.__levels = tuple(
            (round(l[0], 5), int(l[1])) for l in sorted(lev, key=lambda x: x[0])
        )

    def to_openfoam_dict(self):
        """Return data as a dictionary."""
        return {'mode': self.__class__.__name__.lower(),
                'levels': str(self.levels).replace(',', ' ')}

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """representation."""
        return 'mode: {}, levels: {}'.format(
            self.__class__.__name__.lower(),
            str(self.levels).replace(',', ' '))


class Distance(_RefinementMode):
    """Distance refinement mode.

    Attributes:
        levels: A list of (x, y) values for levels. 'levels' specifies per
            distance to the geometry the wanted refinement level.
    """

    pass


class Inside(_RefinementMode):
    """Inside refinement mode.

    Attributes:
        level: Refinement level as an integer. All cells inside the geometry get
            refined up to the level. The geometry needs to be closed for this to
            be possible.
    """

    def __init__(self, level):
        """Create an Inside RefinementMode."""
        # 1.0 will be ignored
        _RefinementMode.__init__(self, ((1.0, int(level)),))

    def __repr__(self):
        """representation."""
        return 'mode: {}, level: {}'.format(
            self.__class__.__name__.lower(), self.levels[0][1])


class Outside(Inside):
    """Outside refinement mode.

    Attributes:
        level: Refinement level as an integer. All cells inside the geometry get
            refined up to the level. The geometry needs to be closed for this to
            be possible.
    """

    pass


def refinement_mode_from_dict(d):
    """Create a Refinement mode from a python dictionary.

    The dictionary should have two keys for model and levels.
    {'levels': '((1.0 4) )', 'mode': 'inside'}
    """
    mode = d['mode']

    levels = str(d['levels']).replace(', ', ' ').replace('( (', '((') \
        .replace(') )', '))')[1:-1].split()

    levels = eval(','.join(levels))

    if mode == 'inside':
        return Inside(levels[-1])
    elif mode == 'outside':
        return Outside(levels[-1])
    elif mode == 'distance':
        return Distance(levels)


def refinementRegions_from_stl_file(filepath, refinement_mode):
    """Create a RefinementRegion form an stl file."""
    geos = bf_geometry_from_stl_file(filepath)
    return tuple(RefinementRegion(geo.name, geo.vertices, geo.face_indices,
                                  geo.normals, refinement_mode)
                 for geo in geos)
