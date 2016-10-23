# coding=utf-8
"""Finite Volume Solution class."""
from foamfile import FoamFile, foamFileFromFile
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

        self.__residualControl = ResidualControl(
            p=self.values['SIMPLE']['residualControl']['p'],
            U=self.values['SIMPLE']['residualControl']['U'],
            k=self.values['SIMPLE']['residualControl']['k'],
            epsilon=self.values['SIMPLE']['residualControl']['epsilon']
        )

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    # TODO: update to pass the recipe itself and not the code!
    @classmethod
    def fromRecipe(cls, recipe=0):
        """Generate fvSolution for a particular recipe.

        Args:
            recipe: 0: incompressible, 1: heat transfer.
        """
        _cls = cls()

        if recipe == 0:
            # steady incompressible
            _values = {
                'solvers': {'p_rgh': None, 'SIMPLE': {'residualControl':
                                                      {'p_rgh': None, 'T': None}},
                            'relaxationFactors': {'p_rgh': None, 'T': None}}
            }

        elif recipe == 1:
            # heat transfer
            _values = {
                'solvers': {'p': None,
                            'p_rgh': {'solver': 'PCG',
                                      'preconditioner': 'DIC',
                                      'tolerance': '1e-08',
                                      'relTol': '0.01'},
                            'T': {'relTol': '0.1', 'tolerance': '1e-8',
                                  'nSweeps': '1', 'smoother': 'GaussSeidel',
                                  'solver': 'smoothSolver'}},
                'SIMPLE': {'residualControl': {'p': None, 'p_rgh': '1e-5',
                                               'T': '1e-5'},
                        #    'pRef': str(_cls.blockMeshDict.center).replace(',', ' '),
                           'pRefValue': '0'},
                'relaxationFactors': {'p': None, 'p_rgh': '0.3', 'T': '0.5'}}

        # update values based on the recipe.
        _cls.updateValues(_values, mute=True)
        return _cls

    @property
    def residualControl(self):
        """Get and set residual controls."""
        return self.__residualControl

    @residualControl.setter
    def residualControl(self, resControl):
        """Set residual control values.

        Args:
            resControl: New residual control.
        """
        if not resControl:
            return

        self.values['SIMPLE']['residualControl']['p'] = str(resControl.p)
        self.values['SIMPLE']['residualControl']['U'] = str(resControl.U)
        self.values['SIMPLE']['residualControl']['k'] = str(resControl.k)
        self.values['SIMPLE']['residualControl']['epsilon'] = str(resControl.epsilon)
        self.__residualControl = resControl

        if resControl.other:
            for key, value in resControl.other.iteritems():
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

    # TODO: Need to check kargs
    def __eq__(self, other):
        """Check equality."""
        if not isinstance(other, self):
            return False

        if float(self.p) != float(other.p):
            return False
        if float(self.U) != float(other.U):
            return False
        if float(self.k) != float(other.k):
            return False
        if float(self.epsilon) != float(other.epsilon):
            return False

        return True

    def __repr__(self):
        """Representation."""
        return "residualControl\n" \
            "{\n\tp     %s;\n\tU     %s;\t\nk     %s;\n\tepsilon     %s;\n" \
            "}" % (self.p, self.U, self.k, self.epsilon)
