"""Finite Volume Solution class."""
from foamfile import FoamFile
from collections import OrderedDict


class FvSolution(FoamFile):
    """Finite Volume Solution class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['solvers'] = OrderedDict()
    __defaultValues['solvers']['p'] = {
        'solver': 'GAMG',
        'tolerance': '1e-7',
        'relTol': '0.1',
        'smoother': 'GaussSeidel',
        'nPreSweepsre': '0',
        'nPostSweeps': '2',
        'cacheAgglomeration': 'on',
        'agglomerator': 'faceAreaPair',
        'nCellsInCoarsestLevel': '10',
        'mergeLevels': '1'
    }

    __defaultValues['solvers']['U'] = {
        'solver': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': '1e-8',
        'relTol': '0.1',
        'nSweeps': '1'
    }

    __defaultValues['solvers']['k'] = {
        'solver': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': '1e-8',
        'relTol': '0.1',
        'nSweeps': '1'
    }

    __defaultValues['solvers']['epsilon'] = {
        'solver': 'smoothSolver',
        'smoother': 'GaussSeidel',
        'tolerance': '1e-8',
        'relTol': '0.1',
        'nSweeps': '1'
    }

    __defaultValues['SIMPLE'] = OrderedDict()
    __defaultValues['SIMPLE']['nNonOrthogonalCorrectors'] = '2'
    __defaultValues['SIMPLE']['residualControl'] = {
        'p': '1e-5',
        'U': '1e-5',
        'k': '1e-5',
        'epsilon': '1e-5'
    }

    __defaultValues['relaxationFactors'] = OrderedDict()
    __defaultValues['relaxationFactors']['p'] = '0.3'
    __defaultValues['relaxationFactors']['U'] = '0.7'
    __defaultValues['relaxationFactors']['k'] = '0.7'
    __defaultValues['relaxationFactors']['epsilon'] = '0.7'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='fvSolution', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    def residualControl(self, p=1e-5, U=1e-5, k=1e-5, epsilon=1e-5, other=None):
        """Set residual control values.

        Args:
            p: Residual control valeus for p (default: 1e-5)
            U: Residual control valeus for U (default: 1e-5)
            k: Residual control valeus for k (default: 1e-5)
            epsilon: Residual control valeus for epsilon (default: 1e-5)
            other: Key values as dictionary for other paramaters (e.g. {'g': 1e-5})
        """
        p = str(p) if p else '1e-5'
        U = str(U) if U else '1e-5'
        k = str(k) if k else '1e-5'
        epsilon = str(epsilon) if epsilon else '1e-5'

        self.values['SIMPLE']['residualControl']['p'] = p
        self.values['SIMPLE']['residualControl']['U'] = U
        self.values['SIMPLE']['residualControl']['k'] = k
        self.values['SIMPLE']['residualControl']['epsilon'] = epsilon

        if other:
            for key, value in other.iteritems():
                self.values['SIMPLE']['residualControl'][str(key)] = str(value)


class ResidualControl(object):
    """Residual Control class.

    Attributes:
        p: Residual control valeus for p (default: 1e-5)
        U: Residual control valeus for U (default: 1e-5)
        k: Residual control valeus for k (default: 1e-5)
        epsilon: Residual control valeus for epsilon (default: 1e-5)
        other: Key values as dictionary for other paramaters (e.g. {'g': 1e-5})
    """

    __slots__ = ('p', 'U', 'k', 'epsilon', 'other')

    def __init__(self, p=1e-5, U=1e-5, k=1e-5, epsilon=1e-5, other=None):
        """Init ResidualControl class."""
        self.p = str(p) if p else 1e-5
        self.U = str(U) if U else 1e-5
        self.k = str(k) if k else 1e-5
        self.epsilon = str(epsilon) if epsilon else 1e-5
        self.other = other if other else None

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Representation."""
        return "ResidualControl\n" \
            "{\n\tp     %s;\n\tU     %s;\t\nk     %s;\n\tepsilon     %s;\n" \
            "}" % (self.p, self.U, self.k, self.epsilon)
