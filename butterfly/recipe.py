# coding=utf-8
"""Butterfly recipes."""
import os
from copy import deepcopy
from .turbulenceProperties import TurbulenceProperties
from .fvSolution import FvSolution, ResidualControl, RelaxationFactors
from .fvSchemes import FvSchemes

from .g import G

# 0 folder objects
from .U import U
from .k import K
from .p import P
from .nut import Nut
from .epsilon import Epsilon
from .T import T
from .alphat import Alphat
from .p_rgh import P_rgh

# TODO: Add checkCase method to prepare a case for the recipe by saving neccasary
# foamfiles for each recipe.Case should write minimum files just for meshing
# and the rest of files will be written once user puts the solution together.
class _Recipe(object):
    """Base class for recipes.

    Attributes:
        commands: A list of OpenFOAM commands. You can pass arguments for each
            command with each command as a string. e.g. ('blockMesh',
            'snappyHexMesh -constant')
        turbulenceProperties: Turbulence properties.
        fvSolution: Optional input for fvSolution to overwrite default fvSolution.
        fvSchemes: Optional input for fvSchemes to overwrite default fvSchemes.
        quantities: A collection of strings for quantities in this solution.
            ('U', 'p', 'k', 'epsilon')
        residualControl: A dictionary of values for residualControl of quantities.
        relaxationFactors: A list of values for relaxationFactors of quantities.
    """
    __foamfilescollection = {'g': G, 'U': U, 'k': K, 'p': P, 'nut': Nut,
                             'epsilon': Epsilon, 'T': T, 'alphat': Alphat,
                             'p_rgh': P_rgh}

    __globalConvergence = 10 ** -4

    def __init__(self, commands, turbulenceProperties, fvSolution=None,
                 fvSchemes=None, quantities=None, residualControl=None, relaxationFactors=None):
        """Initiate recipe."""
        self.commands = commands
        self.turbulanceProprties = turbulenceProperties
        self.fvSolution = fvSolution
        self.fvSchemes = fvSchemes
        self.quantities = quantities
        self.residualControl = residualControl
        self.relaxationFactors = relaxationFactors

    @property
    def isRecipe(self):
        """Return True for recipe."""
        return True

    @property
    def commands(self):
        """List of openfoam commands for this recipe."""
        return self.__commands

    @commands.setter
    def commands(self, cmds):
        """List of openfoam commands for this recipe."""
        if isinstance(cmds, str):
            cmds = (cmds,)

        assert isinstance(cmds, (tuple, list)), \
            'Invalid input for commands: {}. Should be a list or a tuple.' \
            .format(cmds)

        self.__commands = cmds

    @property
    def turbulenceProperties(self):
        """Get the OpenFOAM case."""
        return self.__turbulanceProprties

    @turbulenceProperties.setter
    def turbulencePropertise(self, tp):
        """Update turbulence file for the case."""
        if not tp:
            tp = TurbulenceProperties.RAS()

        assert hasattr(tp, 'isTurbulenceProperties'), \
            'Expected turbulencePropertise not {}.'.format(type(tp))

        self.__turbulenceProperties = tp

    @property
    def fvSolution(self):
        """Get or set fvSolution."""
        return self.__fvSolution

    @fvSolution.setter
    def fvSolution(self, fvsln):
        if fvsln:
            assert hasattr(fvsln, 'isFvSolution'), \
                'fvSolution should be from type FvSolution not {}.' \
                .format(type(fvsln))

        self.__fvSolution = fvsln

    @property
    def fvSchemes(self):
        """Get fvSchemes."""
        return self.__fvSchemes

    @fvSchemes.setter
    def fvSchemes(self, fvschm):
        if fvschm:
            assert hasattr(fvschm, 'isFvSchemes'), \
                'fvSolution should be from type FvSchemes not {}.' \
                .format(type(fvschm))

        self.__fvSchemes = fvschm

    @property
    def quantities(self):
        """List of quantities for the recipe."""
        return self.__quantities

    @quantities.setter
    def quantities(self, q):
        """List of quantities for the recipe."""
        if not q:
            q = ('p', 'U', 'k', 'epsilon')
        else:
            self.__quantities = q

    @property
    def residualControl(self):
        """A dictionary of residuals as quantity: residualValue."""
        return self.__residualControl

    @residualControl.setter
    def residualControl(self, res):
        if res is None:
            res = dict.fromkeys(self.quantities, self.__globalConvergence)

        # check the input to be dictionary and have values for all the input
        # otherwise use default value
        assert isinstance(res, dict), 'residualControl should be a dictionary.'
        self.__residualControl = ResidualControl(res)

    @property
    def relaxationFactors(self):
        """A dictionary of residuals as quantity: residualValue."""
        return self.__relaxationFactors

    @relaxationFactors.setter
    def relaxationFactors(self, relaxFact):
        if relaxFact is None:
            relaxFact = {}

        # check the input to be dictionary and have values for all the input
        # otherwise use default value
        assert isinstance(relaxFact, dict), \
            'relaxationFactors should be a dictionary.'

        self.__relaxationFactors = RelaxationFactors(relaxFact)

    def prepareCase(self, case, overwrite=False, remove=False):
        """Prepare a case for this recipe.

        This method double checks files under Zero folder for each quantities.
        It creates, overwrites or removes the files if needed. Solution class
        calls this method on initialization.

        Args:
            case: A Butterfly case.
            overwrite: Set to True to overwrite current files.
            remove: Set to True to remove extra files in the folder.
        """
        if self.fvSchemes and case.fvSchemes != self.fvSchemes:
            case.fvSchemes = self.fvSchemes
            case.fvSchemes.save(case.projectDir)

        if self.fvSolution and case.fvSolution != self.fvSolution:
            case.fvSolution = self.fvSolution
            case.fvSolution.save(case.projectDir)

        # check neccasary files.
        for q in self.quantities:

            if not hasattr(case, q):
                # try to create the quantity
                assert q in self.__foamfilescollection, \
                    'Failed to find {0} method in {1}.' \
                    '{2} needs {0} foamfile to execute.'.format(
                            q, case, self.__class__.__name__)

                case.__dict__[q] = \
                    self.__foamfilescollection[q].fromBFGeometries(case.geometries)

            case.__dict__[q].save(case.projectDir, overwrite=overwrite)

        # remove extra files.
        if remove:
            for f in os.listdir(case.zeroFolder):
                if f in self.quantities:
                    continue
                if f.endswith('Conditions'):
                    # do not remove ABLConditions and initialConditions
                    continue
                p = os.path.join(case.zeroFolder, f)
                if not os.path.isfile(p):
                    continue
                try:
                    os.remove(p)
                except Exception as e:
                    raise IOError('Unable to remove {}:\n{}'.format(p, e))

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        return '{} Recipe'.format(self.__class__.__name__)


class _SingleCommandRecipe(_Recipe):
    """Recipe for recipe's with a single OpenFOAM command (e.g. simpleFoam).

    Attributes:
        commands: An OpenFOAM command (e.g. 'simpleFoam')
        turbulenceProperties: Turbulence properties.
        fvSolution: Optional input for fvSolution to overwrite default fvSolution.
        fvSchemes: Optional input for fvSchemes to overwrite default fvSchemes.
        quantities: A collection of strings for quantities in this solution.
            ('U', 'p', 'k', 'epsilon')
        residualControl: A dictionary of values for residualControl of quantities.
        relaxationFactors: A list of values for relaxationFactors of quantities.
    """

    def __init__(self, command, turbulenceProperties, fvSolution=None,
                 fvSchemes=None, quantities=None, residualControl=None, relaxationFactors=None):
        """Initiate recipe."""
        _Recipe.__init__(self, (command,), turbulenceProperties, fvSolution,
                         fvSchemes, quantities, residualControl,
                         relaxationFactors)

        self.__command = command

    @property
    def application(self):
        """OpenFOAM application."""
        return self.__command

    def prepareCase(self, case, overwrite=False, remove=False):
        """Prepare a case for this recipe.

        This method sets up the application in control dict and double checks
        files under Zero folder for each quantities. It creates, overwrites or
        removes the files if needed. Solution class calls this method on
        initialization.

        Args:
            case: A Butterfly case.
            overwrite: Set to True to overwrite current files.
            remove: Set to True to remove extra files in the folder.
        """
        # update controlDict
        if case.controlDict.application != self.application:
            case.controlDict.application = self.application
            case.controlDict.save(case.projectDir)

        super(_SingleCommandRecipe, self).prepareCase(case, overwrite, remove)

    @property
    def logFile(self):
        """Return log file name."""
        return '%s.log' % self.application

    @property
    def errFile(self):
        """Return error file name."""
        return '%s.err' % self.application


class SteadyIncompressible(_SingleCommandRecipe):
    """Recipe for Steady Incompressible flows.

    This recipe excutes simpleFoam for the input case.

    Attributes:
        turbulenceProperties: Turbulence properties.
        fvSolution: Optional input for fvSolution to overwrite default fvSolution.
        fvSchemes: Optional input for fvSchemes to overwrite default fvSchemes.
        residualControl: A dictionary of values for residualControl of quantities.
        relaxationFactors: A list of values for relaxationFactors of quantities.
    """

    __command = 'simpleFoam'
    __quantities = ('U', 'p', 'k', 'epsilon')
    __residuals = ('Ux', 'Uy', 'Uz', 'p', 'k', 'epsilon')

    def __init__(self, turbulenceProperties=None, fvSolution=None,
                 fvSchemes=None, residualControl=None, relaxationFactors=None):
        """Initiate recipe."""
        turbulenceProperties = turbulenceProperties or TurbulenceProperties.RAS()

        # add inputs here, and initiate the class.
        fvSolution = fvSolution or FvSolution.fromRecipe(0)
        fvSchemes = fvSchemes or FvSchemes.fromRecipe(0)
        quantities = self.__quantities

        _SingleCommandRecipe.__init__(
                self, self.__command, turbulenceProperties, fvSolution,
                fvSchemes, quantities, residualControl, relaxationFactors)

    @property
    def residuals(self):
        """Values for residual plot."""
        return self.__residuals


class HeatTransfer(_SingleCommandRecipe):
    """Recipe for heat transfer.

    This recipe excutes buoyantBoussinesqSimpleFoam for the input case.

    Attributes:
        turbulenceProperties: Turbulence properties.
        fvSolution: Optional input for fvSolution to overwrite default fvSolution.
        fvSchemes: Optional input for fvSchemes to overwrite default fvSchemes.
        residualControl: A dictionary of values for residualControl of quantities.
        relaxationFactors: A list of values for relaxationFactors of quantities.
    """

    __command = 'buoyantBoussinesqSimpleFoam'
    __quantities = ('U', 'p_rgh', 'T', 'alphat', 'nut', 'k', 'epsilon')
    __residuals = ('Ux', 'Uy', 'Uz', 'p_rgh', 'T')

    def __init__(self, turbulenceProperties=None, fvSolution=None,
                 fvSchemes=None, residualControl=None, relaxationFactors=None):
        """Initiate recipe."""
        turbulenceProperties = turbulenceProperties or TurbulenceProperties.RAS()

        # add inputs here, and initiate the class.
        fvSolution = fvSolution or FvSolution.fromRecipe(1)
        fvSchemes = fvSchemes or FvSchemes.fromRecipe(1)
        quantities = self.__quantities

        _SingleCommandRecipe.__init__(
                self, self.__command, turbulenceProperties, fvSolution,
                fvSchemes, quantities, residualControl, relaxationFactors)

    @property
    def residuals(self):
        """Values for residual plot."""
        return self.__residuals
