# coding=utf-8
"""Butterfly grading class for blockMeshDict."""
from copy import deepcopy


class SimpleGrading(object):
    """Block simpleGrading in blockMeshDict.

    Attributes:
        x_grading: Grading for X. The input can be a Grading or a MultiGrading
            (default: 1).
        y_grading: Grading for Y. The input can be a Grading or a MultiGrading
            (default: 1).
        z_grading: Grading for Z. The input can be a Grading or a MultiGrading
            (default: 1).

    Usage:
        x_grading = Grading.from_expansion_ratio(1)
        y_grading = Grading.from_expansion_ratio(1)
        z_grading = MultiGrading(
            (Grading(0.2, 0.3, 4),
            Grading(0.6, 0.4, 1),
            Grading(0.2, 0.3, 0.25))
        )

        print(simpleGrading(x_grading, y_grading, z_grading))

        >> simpleGrading (
            1.0
            1.0
            (
                (0.2 0.3 4.0)
                (0.6 0.4 1.0)
                (0.2 0.3 0.25)
            )
            )
    """

    def __init__(self, x_grading=1, y_grading=1, z_grading=1):
        """Init simpleGrading class."""
        self.x_grading = self._try_read_grading(x_grading)
        self.y_grading = self._try_read_grading(y_grading)
        self.z_grading = self._try_read_grading(z_grading)

    @property
    def isSimpleGrading(self):
        """Return True."""
        return True

    def _try_read_grading(self, g):
        """Try to convert input value to grading."""
        if hasattr(g, 'isGrading'):
            assert g.is_valid, \
                'You cannot use grading {} as a single grading.' \
                'Use this grading to create a MultiGrading and then use' \
                'MultiGrading to create simpleGrading.'.format(g)
            return g
        elif str(g).isdigit():
            # create grading from a single value as expansion ratio
            return Grading.from_expansion_ratio(g)
        else:
            try:
                return Grading(*tuple(g))
            except Exception as e:
                raise ValueError('Invalid input ({}). Grading should be a number '
                                 'or a tuple of numeric values.\n{}'.format(g, e))

    def to_openfoam(self):
        """Get blockMeshDict string.

        Args:
            vertices: list of vertices for all the geometries in the case.
            tolerance: Distance tolerance between input vertices and blockMesh
                vertices.
        """
        _body = "\nsimpleGrading (\n\t{}\n\t{}\n\t{}\n\t)"

        return _body.format(self.x_grading, self.y_grading, self.z_grading)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM blockMeshDict boundary."""
        return self.to_openfoam()


class MultiGrading(object):
    """MultiGrading.

    Use this object to create MultiGrading like the example below.
        (0.2 0.3 4)    // 20% y-dir, 30% cells, expansion = 4
        (0.6 0.4 1)    // 60% y-dir, 40% cells, expansion = 1
        (0.2 0.3 0.25) // 20% y-dir, 30% cells, expansion = 0.25 (1/4)
    Read more at section 5.3.1.3: http://cfd.direct/openfoam/user-guide/blockmesh/

    Attributes:
        gradings: A list of minimum two OpenFOAM Gradings. All the gradings
            should have percentage_length and percentage_cells values.
    """

    def __init__(self, gradings):
        """Init MultiGrading."""
        assert len(gradings) > 1, 'Length of gradings should be at least 2.'

        for g in gradings:
            assert hasattr(g, 'isGrading') and g.percentage_cells \
                and g.percentage_length, 'Invalid input: {}'.format(g)

        self.__gradings = gradings

    @property
    def gradings(self):
        """Get gradings in this MultiGrading."""
        return self.__gradings

    @property
    def isGrading(self):
        """Return True."""
        return True

    @property
    def isMultiGrading(self):
        """Return True."""
        return True

    @property
    def is_valid(self):
        """Return True."""
        return True

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """MultiGrading."""
        return '(\n\t\t{}\n\t)'.format('\n\t\t'.join(map(str, self.gradings)))


class Grading(object):
    """OpenFOAM grading.

    Use this class to create OpenFOAM grading with either a single expansion
    ration or (percentage_length, percentage_cells, expansion_ratio).

    Attributes:
        percentage_length: Percentage of length of the block.
        percentage_cells: Percentage of cells to be included in this segment.
        expansion_ratio: Expansion ration in this segment (default: 1).
    """

    def __init__(self, percentage_length=None, percentage_cells=None,
                 expansion_ratio=1):
        """Init a grading."""
        self.percentage_length = self._check_values(percentage_length)
        self.percentage_cells = self._check_values(percentage_cells)
        self.expansion_ratio = self._check_values(expansion_ratio)

    @classmethod
    def from_expansion_ratio(cls, expansion_ratio=1):
        """Create a grading with only expansion_ratio."""
        return cls(expansion_ratio=expansion_ratio)

    @staticmethod
    def _check_values(v):
        if not v:
            return
        try:
            return float(v)
        except TypeError:
            return int(v)

    @property
    def isGrading(self):
        """Return True."""
        return True

    @property
    def is_valid(self):
        """Return True if grading is just an expansion_ratio."""
        return not self.percentage_cells or not self.percentage_length

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Grading."""
        if not self.percentage_cells or not self.percentage_length:
            return str(self.expansion_ratio)
        else:
            return '({} {} {})'.format(self.percentage_length,
                                       self.percentage_cells,
                                       self.expansion_ratio)
