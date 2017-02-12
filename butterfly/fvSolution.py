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
    __defaultValues['SIMPLE']['residualControl'] = {}

    __defaultValues['relaxationFactors'] = {}
    __defaultValues['relaxationFactors']['p'] = '0.3'
    __defaultValues['relaxationFactors']['U'] = '0.7'
    __defaultValues['relaxationFactors']['k'] = '0.7'
    __defaultValues['relaxationFactors']['epsilon'] = '0.7'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='fvSolution', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    # TODO(): update to pass the recipe itself and not the code!
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
                'solvers': {'p_rgh': None, 'T': None},
                'SIMPLE': {'residualControl': {'p_rgh': None, 'T': None}},
                'relaxationFactors': {'p_rgh': None, 'T': None}
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
                'SIMPLE': {'residualControl': {'p': None, 'p_rgh': '1e-4',
                                               'T': '1e-4'},
                           'pRefPoint': '(0 0 0)', 'pRefValue': '0'},
                'relaxationFactors': {'p': None, 'p_rgh': '0.3', 'T': '0.5'}}

        # update values based on the recipe.
        _cls.updateValues(_values, mute=True)
        return _cls

    @property
    def residualControl(self):
        """Get and set residual controls."""
        return ResidualControl(self.values['SIMPLE']['residualControl'])

    @residualControl.setter
    def residualControl(self, resControl):
        """Set residual control values.

        Args:
            resControl: New residual control.
        """
        if not resControl:
            return

        if not self.values['SIMPLE']['residualControl']:
            self.values['SIMPLE']['residualControl'] = {}

        for key, value in resControl.values.iteritems():
            self.values['SIMPLE']['residualControl'][str(key)] = str(value)

    @property
    def relaxationFactors(self):
        """Get and set residual controls."""
        return RelaxationFactors(self.values['relaxationFactors'])

    @relaxationFactors.setter
    def relaxationFactors(self, relaxFact):
        """Set residual control values.

        Args:
            resControl: New residual control.
        """
        if not relaxFact:
            return

        if not self.values['relaxationFactors']:
            self.values['relaxationFactors'] = {}

        for key, value in relaxFact.values.iteritems():
            self.values['relaxationFactors'][str(key)] = str(value)


# TODO(Mostapha): This is not critical but it will be cleaner if I can find a
# solution to keep ResidualControl as a subclass of dict and still get it to
# work in Grasshopper and Dynamo.
class ResidualControl(object):
    """Residual Control class.

    Attributes:
        values: Values as a dictionary.
    """

    __slots__ = ('values',)

    def __init__(self, values):
        """Init ResidualControl class."""
        if not values:
            self.values = {}
        else:
            self.values = values

    @property
    def isResidualControl(self):
        """Return True."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Representation."""
        return 'residualControl\n{\n\t%s\n}' % (
            '\n\t'.join(('{}\t{};'.format(k, v) for k, v in self.values.iteritems())))


class RelaxationFactors(object):
    """relaxationFactors class.

    Attributes:
        values: Values as a dictionary.
    """

    __slots__ = ('values',)

    def __init__(self, values):
        """Init relaxationFactors class."""
        if not values:
            self.values = {}
        else:
            self.values = values

    @property
    def isRelaxationFactors(self):
        """Return True."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Representation."""
        return 'relaxationFactors\n{\n\t%s\n}' % (
            '\n\t'.join(('{}\t{};'.format(k, v) for k, v in self.values.iteritems())))
