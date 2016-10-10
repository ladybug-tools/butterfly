# coding=utf-8
"""Butterfly recipes."""
import os
from copy import deepcopy
from .turbulenceProperties import TurbulenceProperties
from .fvSolution import FvSolution


class _BFRecipe(object):
    """Base class for recipes.

    Attributes:
        case: An OpenFOAM Case.
        turbulenceProperties: Turbulence properties.
    """

    def __init__(self, case, turbulenceProperties):
        """Initiate recipe."""
        self.__case = case
        self.__turbulanceProprties = turbulenceProperties
        self.__updateTurbulencePropertise()

    @property
    def case(self):
        """Get the OpenFOAM case."""
        return self.__case

    @property
    def logFile(self):
        """Return address of the log file."""
        raise NotImplementedError('abstractproperty.')

    @property
    def errFile(self):
        """Return address of the error file."""
        raise NotImplementedError('abstractproperty.')

    @property
    def turbulenceProperties(self):
        """Get the OpenFOAM case."""
        return self.__turbulanceProprties

    @property
    def quantities(self):
        """Important Quantities for the recipe."""
        raise NotImplementedError('abstractproperty.')

    def __updateTurbulencePropertise(self):
        """Update turbulence file for the case."""
        self.case.turbulenceProperties = self.turbulenceProperties
        try:
            self.case.turbulenceProperties.save(self.case.projectDir)
        except Exception as e:
            raise Exception(
                'Failed to update the turbulence Properties:\n{}'.format(e))

    def run(self):
        """Execute the recipe."""
        raise NotImplementedError('abstractmethod.')

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        return '{} Recipe'.format(self.__class__.__name__)


class _BFSingleApplicationRecipe(_BFRecipe):
    """Recipe for recipe's with a single application (e.g. simpleFoam).

    This recipe excutes application for the input case.

    Attributes:
        case: An OpenFOAM Case.
        application: Application name for this recipe. The application will
            be set up in controlDict.
        turbulenceProperties: Turbulence properties.
    """

    def __init__(self, case, application, turbulenceProperties=None):
        """Initiate recipe."""
        if not turbulenceProperties:
            turbulenceProperties = TurbulenceProperties.RAS()

        _BFRecipe.__init__(self, case, turbulenceProperties)

        self.application = application

        # update application
        case.controlDict.application = application
        case.controlDict.save(case.projectDir)

    @property
    def residualFile(self):
        """Return address of the residual file."""
        return os.path.join(self.case.etcDir, '%s.log' % self.application)

    @property
    def logFile(self):
        """Return address of the log file."""
        return os.path.join(self.case.etcDir, '%s.log' % self.application)

    @property
    def errFile(self):
        """Return address of the error file."""
        return os.path.join(self.case.etcDir, '%s.err' % self.application)

    @property
    def quantities(self):
        """Important Quantities for the recipe."""
        return NotImplementedError()

    def run(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Execute the recipe."""
        return getattr(self.case, self.application)(args, decomposeParDict, run, wait)


class SteadyIncompressible(_BFSingleApplicationRecipe):
    """Recipe for Steady Incompressible flows.

    This recipe excutes simpleFoam for the input case.

    Attributes:
        case: An OpenFOAM Case.
        turbulenceProperties: Turbulence properties.
    """

    def __init__(self, case, turbulenceProperties=None):
        """Initiate recipe."""
        if not turbulenceProperties:
            turbulenceProperties = TurbulenceProperties.RAS()

        _BFSingleApplicationRecipe.__init__(self, case, 'simpleFoam',
                                            turbulenceProperties)

        # update fvSolution
        self.case.fvSolution = FvSolution.fromRecipe(0)
        self.case.fvSolution.save(self.case.projectDir)

    @property
    def quantities(self):
        """Important Quantities for the recipe."""
        return ('Ux', 'Uy', 'Uz', 'p', 'k', 'epsilon')


class HeatTransfer(_BFSingleApplicationRecipe):
    """Recipe for Steady Incompressible flows.

    This recipe excutes simpleFoam for the input case.

    Attributes:
        case: An OpenFOAM Case.
        turbulenceProperties: Turbulence properties.
    """

    def __init__(self, case, turbulenceProperties=None):
        """Initiate recipe."""
        if not turbulenceProperties:
            turbulenceProperties = TurbulenceProperties.RAS()

        _BFSingleApplicationRecipe.__init__(self, case,
                                            'buoyantBoussinesqSimpleFoam',
                                            turbulenceProperties)

        # update fvSolution
        self.case.fvSolution = FvSolution.fromRecipe(1)
        self.case.fvSolution.save(self.case.projectDir)

        # write g, T, p_rgh, alphat
        self.case.g.save(self.case.projectDir)
        self.case.T.save(self.case.projectDir)
        self.case.p_rgh.save(self.case.projectDir)
        self.case.alphat.save(self.case.projectDir)

    @property
    def quantities(self):
        """Important Quantities for the recipe."""
        return ('Ux', 'Uy', 'Uz', 'p_rgh', 'T')
