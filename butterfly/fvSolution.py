"BlockMeshDict class."
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

    __defaultValues['SIMPLE'] = {}
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


fv = FvSolution()
fv.save(r'C:\Users\Administrator\butterfly\innerflow_3')
