"""Butterfly recipes."""
import os
from copy import deepcopy
from .turbulenceProperties import TurbulenceProperties


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


class SteadyIncompressible(_BFRecipe):
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

        _BFRecipe.__init__(self, case, turbulenceProperties)

        # update application
        case.controlDict.application = 'simpleFoam'
        case.controlDict.save(case.projectDir)

    @property
    def residualFile(self):
        """Return address of the residual file."""
        return os.path.join(self.case.etcDir, 'simpleFoam.log')

    @property
    def logFile(self):
        """Return address of the log file."""
        return os.path.join(self.case.etcDir, 'simpleFoam.log')

    @property
    def errFile(self):
        """Return address of the error file."""
        return os.path.join(self.case.etcDir, 'simpleFoam.err')

    @property
    def quantities(self):
        """Important Quantities for the recipe."""
        return ('Ux', 'Uy', 'Uz', 'p', 'k', 'epsilon')

    def run(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Execute the recipe."""
        return self.case.simpleFoam(args, decomposeParDict, run, wait)
