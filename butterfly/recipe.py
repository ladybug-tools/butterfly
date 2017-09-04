# coding=utf-8
"""Butterfly recipes."""
import os
from copy import deepcopy
from .turbulence_properties import TurbulenceProperties
from .transport_properties import TransportProperties
from .fv_solution import FvSolution, ResidualControl, RelaxationFactors
from .fv_schemes import FvSchemes

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


class _Recipe(object):
    """Base class for recipes.

    Attributes:
        commands: A list of OpenFOAM commands. You can pass arguments for each
            command with each command as a string. e.g. ('blockMesh',
            'snappyHexMesh -constant')
        turbulence_properties: Turbulence properties.
        fv_solution: Optional input for fv_solution to overwrite default fv_solution.
        fv_schemes: Optional input for fv_schemes to overwrite default fv_schemes.
        quantities: A collection of strings for quantities in this solution.
            ('U', 'p', 'k', 'epsilon')
        residual_control: A dictionary of values for residual_control of quantities.
        relaxation_factors: A list of values for relaxation_factors of quantities.
    """

    __foamfilescollection = {'g': G, 'U': U, 'k': K, 'p': P, 'nut': Nut,
                             'epsilon': Epsilon, 'T': T, 'alphat': Alphat,
                             'p_rgh': P_rgh,
                             'transport_properties': TransportProperties}

    __globalConvergence = 10 ** -4

    def __init__(self, commands, turbulence_properties, fv_solution=None,
                 fv_schemes=None, quantities=None, residual_control=None,
                 relaxation_factors=None):
        """Initiate recipe."""
        self.commands = commands
        self.turbulence_properties = turbulence_properties
        self.fv_solution = fv_solution
        self.fv_schemes = fv_schemes
        self.quantities = quantities
        self.residual_control = residual_control
        self.relaxation_factors = relaxation_factors

    @property
    def is_recipe(self):
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
    def turbulence_properties(self):
        """Get the OpenFOAM case."""
        return self.__turbulence_properties

    @turbulence_properties.setter
    def turbulence_properties(self, tp):
        """Update turbulence file for the case."""
        if not tp:
            tp = TurbulenceProperties.RAS()

        assert hasattr(tp, 'isTurbulenceProperties'), \
            'Expected turbulencePropertise not {}.'.format(type(tp))

        self.__turbulence_properties = tp

    @property
    def fv_solution(self):
        """Get or set fv_solution."""
        return self.__fv_solution

    @fv_solution.setter
    def fv_solution(self, fvsln):
        if fvsln:
            assert hasattr(fvsln, 'isFvSolution'), \
                'fv_solution should be from type FvSolution not {}.' \
                .format(type(fvsln))

        self.__fv_solution = fvsln

    @property
    def fv_schemes(self):
        """Get fv_schemes."""
        return self.__fv_schemes

    @fv_schemes.setter
    def fv_schemes(self, fvschm):
        if fvschm:
            assert hasattr(fvschm, 'isFvSchemes'), \
                'fv_solution should be from type FvSchemes not {}.' \
                .format(type(fvschm))

        self.__fv_schemes = fvschm

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
    def residual_control(self):
        """A dictionary of residuals as quantity: residualValue."""
        return self.__residual_control

    @residual_control.setter
    def residual_control(self, res):
        if res is None:
            res = dict.fromkeys(self.quantities, self.__globalConvergence)

        # check the input to be dictionary and have values for all the input
        # otherwise use default value
        if isinstance(res, dict):
            self.__residual_control = ResidualControl(res)
        elif isinstance(res, ResidualControl):
            self.__residual_control = res
        else:
            raise TypeError(
                'residual_control should be a dictionary not a {}.'.format(type(res))
            )
        # update fv_solution
        self.fv_solution.residual_control = self.residual_control

    @property
    def relaxation_factors(self):
        """A dictionary of residuals as quantity: residualValue."""
        return self.__relaxation_factors

    @relaxation_factors.setter
    def relaxation_factors(self, relax_fact):
        if relax_fact is None:
            relax_fact = {}

        # check the input to be dictionary and have values for all the input
        # otherwise use default value
        if isinstance(relax_fact, dict):
            self.__relaxation_factors = RelaxationFactors(relax_fact)
        elif isinstance(relax_fact, RelaxationFactors):
            self.__relaxation_factors = relax_fact
        else:
            raise TypeError(
                'relaxation_factors should be a dictionary not a {}.'
                .format(type(relax_fact))
            )

        # update fv_solution
        self.fv_solution.relaxation_factors = self.relaxation_factors

    def prepare_case(self, case, overwrite=False, remove=False):
        """Prepare a case for this recipe.

        This method double checks files under Zero folder for each quantities.
        It creates, overwrites or removes the files if needed. Solution class
        calls this method on initialization.

        Args:
            case: A Butterfly case.
            overwrite: Set to True to overwrite current files.
            remove: Set to True to remove extra files in the folder.
        """
        print('Preparing {} for {} study...'.format(case, self.__class__.__name__))

        if self.fv_schemes and case.fv_schemes != self.fv_schemes:
            case.fv_schemes = self.fv_schemes
            case.fv_schemes.save(case.project_dir)

        if self.fv_solution and case.fv_solution != self.fv_solution:
            case.fv_solution = self.fv_solution
            case.fv_solution.save(case.project_dir)

        if self.turbulence_properties and \
                case.turbulence_properties != self.turbulence_properties:
            case.turbulence_properties = self.turbulence_properties
            case.turbulence_properties.save(case.project_dir)

        if case.decomposeParDict:
            case.decomposeParDict.save(case.project_dir)

        if hasattr(case, 'probes'):
            case.probes.save(case.project_dir)

        if hasattr(case, 'ABLConditions'):
            case.ABLConditions.save(case.project_dir, overwrite=overwrite)

        if hasattr(case, 'initial_conditions'):
            case.initial_conditions.save(case.project_dir, overwrite=overwrite)

        # check neccasary files.
        for q in (self.quantities + ('transport_properties', 'g')):

            if not hasattr(case, q):
                # try to create the quantity
                assert q in self.__foamfilescollection, \
                    'Failed to find {0} method in {1}.' \
                    '{2} needs {0} foamfile to execute.'.format(
                        q, case, self.__class__.__name__)

                case.__dict__[q] = \
                    self.__foamfilescollection[q].from_bf_geometries(case.geometries)

            case.__dict__[q].save(case.project_dir, overwrite=overwrite)

        # remove extra files.
        if remove:
            for f in os.listdir(case.zero_folder):
                if f in self.quantities:
                    continue
                if f.endswith('Conditions'):
                    # do not remove ABLConditions and initial_conditions
                    continue
                p = os.path.join(case.zero_folder, f)
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
        turbulence_properties: Turbulence properties.
        fv_solution: Optional input for fv_solution to overwrite default fv_solution.
        fv_schemes: Optional input for fv_schemes to overwrite default fv_schemes.
        quantities: A collection of strings for quantities in this solution. A
            separate file will be created in 0 folder for each quantity.
        residual_control: A dictionary of values for residual_control of residuals.
        relaxation_factors: A list of values for relaxation_factors of residuals.
        residual_fields: List of quantities that should be watched during solution
            run ('Ux', 'Uy', 'Uz', 'p', 'k', 'epsilon').
    """

    def __init__(self, command, turbulence_properties, fv_solution=None,
                 fv_schemes=None, quantities=None, residual_control=None,
                 relaxation_factors=None, residual_fields=None):
        """Initiate recipe."""
        _Recipe.__init__(self, (command,), turbulence_properties, fv_solution,
                         fv_schemes, quantities, residual_control,
                         relaxation_factors)

        self.__command = command
        self.__residual_fields = residual_fields or ('p')

    @property
    def application(self):
        """OpenFOAM application."""
        return self.__command

    def prepare_case(self, case, overwrite=False, remove=False):
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
            case.controlDict.save(case.project_dir)

        super(_SingleCommandRecipe, self).prepare_case(case, overwrite, remove)

    @property
    def residual_fields(self):
        """List of values for residual plot."""
        return self.__residual_fields

    @property
    def log_file(self):
        """Return log file name."""
        return '%s.log' % self.application

    @property
    def err_file(self):
        """Return error file name."""
        return '%s.err' % self.application


class SteadyIncompressible(_SingleCommandRecipe):
    """Recipe for Steady Incompressible flows.

    This recipe excutes simpleFoam for the input case.

    Attributes:
        turbulence_properties: Turbulence properties.
        fv_solution: Optional input for fv_solution to overwrite default fv_solution.
        fv_schemes: Optional input for fv_schemes to overwrite default fv_schemes.
        residual_control: A dictionary of values for residual_control of quantities.
        relaxation_factors: A list of values for relaxation_factors of quantities.
    """

    __command = 'simpleFoam'
    # foam files in zero folder
    __quantities = ('epsilon', 'k', 'nut', 'U', 'p')
    # Values for residual plot.
    __residual_fields = ('Ux', 'Uy', 'Uz', 'p', 'k', 'epsilon')

    def __init__(self, turbulence_properties=None, fv_solution=None,
                 fv_schemes=None, residual_control=None, relaxation_factors=None):
        """Initiate recipe."""
        turbulence_properties = turbulence_properties or TurbulenceProperties.RAS()
        # add inputs here, and initiate the class.
        fv_solution = fv_solution or FvSolution.from_recipe(0)
        fv_schemes = fv_schemes or FvSchemes.from_recipe(0)
        quantities = self.__quantities

        _SingleCommandRecipe.__init__(
            self, self.__command, turbulence_properties, fv_solution, fv_schemes,
            quantities, residual_control, relaxation_factors, self.__residual_fields)


class HeatTransfer(_SingleCommandRecipe):
    """Recipe for heat transfer.

    This recipe excutes buoyantBoussinesqSimpleFoam for the input case.

    Attributes:
        turbulence_properties: Turbulence properties.
        fv_solution: Optional input for fv_solution to overwrite default fv_solution.
        fv_schemes: Optional input for fv_schemes to overwrite default fv_schemes.
        residual_control: A dictionary of values for residual_control of quantities.
        relaxation_factors: A list of values for relaxation_factors of quantities.
    """

    __command = 'buoyantBoussinesqSimpleFoam'
    # foam files in zero folder
    __quantities = ('alphat', 'epsilon', 'k', 'nut', 'p_rgh', 'T', 'U')
    # values for residual plot.
    __residual_fields = ('Ux', 'Uy', 'Uz', 'p_rgh', 'T', 'k', 'epsilon')

    def __init__(self, turbulence_properties=None, fv_solution=None,
                 fv_schemes=None, residual_control=None, relaxation_factors=None,
                 t_ref=None):
        """Initiate recipe."""
        turbulence_properties = turbulence_properties or TurbulenceProperties.RAS()

        # add inputs here, and initiate the class.
        fv_solution = fv_solution or FvSolution.from_recipe(1)
        fv_schemes = fv_schemes or FvSchemes.from_recipe(1)
        self.temperature = t_ref or 300
        quantities = self.__quantities

        _SingleCommandRecipe.__init__(
            self, self.__command, turbulence_properties, fv_solution, fv_schemes,
            quantities, residual_control, relaxation_factors, self.__residual_fields)

    def prepare_case(self, case, overwrite=False, remove=False):
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
        # update pRefPoint to center location_in_mesh for snappyHexMeshDict
        self.fv_solution.values['SIMPLE']['pRefPoint'] = \
            str(case.snappy_hex_meshDict.location_in_mesh).replace(',', ' ')

        # updated t_ref if it is provided
        case.T.update_values({'internalField': 'uniform %f' % self.temperature})

        super(HeatTransfer, self).prepare_case(case, overwrite, remove)
