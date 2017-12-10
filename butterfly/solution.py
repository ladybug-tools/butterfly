# coding=utf-8
"""Butterfly Solution."""
from copy import deepcopy
from collections import namedtuple, OrderedDict
import os

from .utilities import tail, load_skipped_probes
from .parser import CppDictParser


class Solution(object):
    """Butterfly Solution.

    This class creates a solution from a recipe which is ready to run and monitor.

    Args:
        case: A butterfly case.
        recipe: A butterfly recipe.
        decomposeParDict: decomposeParDict for parallel run (default: None).
        solution_parameter: A SolutionParameter (default: None).
        remove_extra_foam_files: set to True if you want butterfly to remove all the
            extra files in 0 folder once you update the recipe (default: False).
    """

    def __init__(self, case, recipe, decomposeParDict=None, solution_parameter=None,
                 remove_extra_foam_files=False):
        """Init solution."""
        self.__remove = remove_extra_foam_files
        assert hasattr(case, 'isCase'), \
            'ValueError:: {} is not a Butterfly.Case'.format(case)
        self.decomposeParDict = decomposeParDict

        self.__case = case
        self.case.decomposeParDict = self.decomposeParDict

        self.recipe = recipe
        self.update_solution_params(solution_parameter)
        # set internal properties for running the solution

        # place holder for residuals
        self.__residualValues = OrderedDict.fromkeys(self.residual_fields, 0)
        self.__isRunStarted = False
        self.__isRunFinished = False
        self.__process = None
        self.__log_files = None
        self.__errFiles = None

    @property
    def project_name(self):
        """Get porject name."""
        return self.case.project_name

    @property
    def case(self):
        """Case."""
        return self.__case

    @property
    def recipe(self):
        """Get recipe."""
        return self.__recipe

    @recipe.setter
    def recipe(self, r):
        """set recipe."""
        assert hasattr(r, 'isRecipe'), '{} is not a recipe.'.format(r)
        self.__recipe = r
        self.__recipe.prepare_case(self.case, overwrite=True,
                                   remove=self.__remove)

    @property
    def decomposeParDict(self):
        """DecomposeParDict."""
        return self.__decomposeParDict

    @decomposeParDict.setter
    def decomposeParDict(self, dpd):
        """Set decomposeParDict."""
        if dpd:
            assert hasattr(dpd, 'isDecomposeParDict'), \
                '{} is not a DecomposeParDict.'.format(dpd)
        self.__decomposeParDict = dpd

    @property
    def remove_extra_foam_files(self):
        """If True, solution will remove extra files everytime recipe changes."""
        return self.__remove

    @property
    def project_dir(self):
        """Get project directory."""
        return self.case.project_dir

    @property
    def residual_fields(self):
        """Get list of residuals to be watched during the run."""
        return self.recipe.residual_fields

    @property
    def controlDict(self):
        """Get controlDict."""
        return self.__case.controlDict

    @property
    def residualControl(self):
        """Get residualControl values for this solution."""
        return self.__case.fvSolution.residualControl

    @property
    def probes(self):
        """Get probes if any."""
        return self.__case.probes

    @property
    def residual_file(self):
        """Return address of the residual file."""
        return os.path.join(self.case.log_folder, self.recipe.log_file)

    @property
    def log_files(self):
        """Get full path to log files."""
        return self.__log_files

    @property
    def log(self):
        """Get the log report."""
        isContent, content = self.case.runmanager.check_file_contents(self.log_files)

    @property
    def err_files(self):
        """Get full path to error files."""
        return self.__errFiles

    @property
    def is_running(self):
        """Check if the solution is still running."""
        if not self.__isRunStarted and not self.__isRunFinished:
            return False
        elif self.__process.poll() is None:
            return True
        else:
            self.__isRunFinished = True
            self.case.rename_snappyHexMesh_folders()
            # load errors if any
            self.case.runmanager.check_file_contents(self.log_files)
            failed, err = self.case.runmanager.check_file_contents(self.err_files)

            assert not failed, err

    @property
    def timestep(self):
        """Get latest timestep for this solution."""
        return self.__get_latestTime()

    @property
    def residual_values(self, latestTime=True):
        """Get timestep and residual values as a tuple."""
        if latestTime:
            return self.__get_info().residual_values
        else:
            raise NotImplementedError()

    @property
    def info(self):
        """Get timestep and residual values as a tuple."""
        return self.__get_info()

    def __get_info(self):
        i = namedtuple('Info', 'timestep residualValues')
        # get end of the log file
        if not os.path.isfile(self.residual_file):
            return i(0, self.__residualValues.values())

        text = tail(self.residual_file).split("\nTime =")[-1].split('\n')
        # get timestep
        try:
            t = int(text[0])
        except ValueError:
            t = 0

        # read residual values
        for line in text:
            try:
                # quantity, Initial residual, Final residual, No Iterations
                q, ir, fr, ni = line.split(':  Solving for ')[1].split(',')
                # use final residual
                if q in self.__residualValues:
                    self.__residualValues[q] = ir.split('= ')[-1]
            except IndexError:
                pass

        return i(t, self.__residualValues.values())

    def __get_latestTime(self):
        # get end of the log file
        if not os.path.isfile(self.residual_file):
            return 0
        text = tail(self.residual_file).split("\nTime =")[-1].split('\n')
        # get timestep
        try:
            t = int(text[0])
        except ValueError:
            t = 0
        return t

    def update_from_recipe(self, recipe):
        """Update solution from recipe inputs.

        This method creates a SolutionParameter from each recipe property, and
        uses updateSolutionParams to update the solution.
        """
        tp = SolutionParameter.from_cpp_dictionary('turbulenceProperties',
                                                   str(recipe.turbulenceProperties))
        fv_sc = SolutionParameter.from_cpp_dictionary('fvSchemes',
                                                      str(recipe.fvSchemes))
        fv_sol = SolutionParameter.from_cpp_dictionary('fvSolution',
                                                       str(recipe.fvSolution))

        self.update_solution_params((tp, fv_sc, fv_sol))

    def update_solution_params(self, sol_params, timestep=None):
        """Update parameters.

        Attributes:
            sol_params: A list of solution parameters.
        """
        if not sol_params:
            # if input is None return
            return
        # check input with the current and update them if there has been changes
        for solPar in sol_params:
            assert hasattr(solPar, 'isSolutionParameter'), \
                '{} is not a solution parameter.'.format(solPar)

            # check if this timestep in range of SolutionParameter time range
            if timestep is not None and not solPar.is_time_in_range(timestep):
                # not in time range! try the next one
                continue

            try:
                update = getattr(self.__case, solPar.filename) \
                    .update_values(solPar.values, solPar.replace)
            except AttributeError as e:
                # probes can be empty at start
                raise AttributeError(e)

            # check to remove functions if needed
            if solPar.filename == 'controlDict':
                cur_func = self.__case.controlDict.values['functions'].keys()
                new_func = solPar.values['functions'].keys()

                for k in cur_func:
                    if k not in new_func:
                        del(self.__case.controlDict.values['functions'][k])
                        update = True

            if update:
                print('Updating {}...'.format(solPar.filename))
                ffile = getattr(self.__case, solPar.filename)
                ffile.save(self.project_dir)

                # just in case probes was not there and now should be included
                # in controlDict
                if solPar.filename == 'probes':
                    if not self.controlDict.include:
                        self.controlDict.include = solPar.filename
                        self.controlDict.save(self.project_dir)

    def run(self, wait=False):
        """Execute the solution."""
        self.case.rename_snappyHexMesh_folders()
        log = self.case.command(
            cmd=self.recipe.application,
            args=None,
            decomposeParDict=self.__decomposeParDict,
            run=True, wait=wait)
        self.__process = log.process
        self.__errFiles = log.errorfiles
        self.__log_files = log.logfiles
        self.__isRunStarted = True
        if not wait:
            self.__isRunFinished = False
        else:
            self.__isRunFinished = True

    def purge(self, remove_polyMesh_content=True,
              remove_snappyHexMesh_folders=True,
              remove_result_folders=False,
              remove_postProcessing_folder=False):
        """Purge solution's case folder."""
        self.case.purge(
            remove_polyMesh_content, remove_snappyHexMesh_folders,
            remove_result_folders, remove_postProcessing_folder)

    def terminate(self):
        """Cancel the solution."""
        self.case.runmanager.terminate()
        if self.decomposeParDict:
            # remove processor folders if they haven't been removed already.
            self.case.remove_processor_folders()

    def load_probe_values(self, field):
        """Return OpenFOAM probes results for a given field (e.g. U)."""
        return self.case.load_probe_values(field)

    def load_probes(self, field):
        """Return OpenFOAM probes location for a given field (e.g. U)."""
        return self.case.load_probes(field)

    def skipped_probes(self):
        """Get list of probes that are skipped from the solution."""
        return load_skipped_probes(os.path.join(self.case.log_folder,
                                                self.recipe.log_file))

    def sample(self, name, points, field, wait=True):
        """Sample the results for a certain field.

        Args:
            name: A unique name for this sample.
            points: List of points as (x, y, z).
            fields: List of fields (e.g. U, p).
            args: Command arguments.
            wait: Wait until command execution ends.
        Returns:
            namedtuple(probes, values).
        """
        return self.case.sample(name, points, field, wait=True)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Solution representation."""
        return "{}::{}".format(self.project_name, self.recipe)


class SolutionParameter(object):
    """A solution parameter that can be changed during the solution.

    Add solution parameter to to solution settings.

    Attributes:
        filename: OpenFOAM filename that the values are belong to (e.g.
            blockMeshDict, fvSchemes).
        values: New values as a python dictionary.
        replace: Set to True if you want the original dictionary to be replaced
            by new values. Default is False which means the original dictionary
            will be only updated by new values.
        time_range: Time range that this SolutioParameter is valid as a tuple
            (default: (0, 1.0e+100)).
    """

    _of_filenames = ('epsilon', 'k', 'nut', 'p', 'U', 'T', 'turbulenceProperties',
                     'transportProperties', 'blockMeshDict', 'controlDict',
                     'fvSchemes', 'fvSolution', 'snappyHexMeshDict', 'probes')

    def __init__(self, of_filename, values, replace=False, time_range=None):
        """Create solution parameter."""
        self.filename = of_filename
        self.values = values
        self.replace = replace

        try:
            self.__t0 = int(time_range[0])
            self.__t1 = int(time_range[1])
        except TypeError:
            self.__t0, self.__t1 = 0, 1.0e+100
        except ValueError:
            self.__t0, self.__t1 = 0, 1.0e+100

    @classmethod
    def from_dictionary_file(cls, of_filename, filepath, replace=False,
                             time_range=None):
        """Create from an OpenFOAM dictionary file."""
        # convert values to python dictionary
        values = CppDictParser.from_file(filepath).values
        return cls(of_filename, values, replace, time_range)

    @classmethod
    def from_cpp_dictionary(cls, of_filename, dictionary, replace=False,
                            time_range=None, header=False):
        """Create from an OpenFOAM dictionary in text format."""
        # convert values to python dictionary
        values = CppDictParser(text=dictionary).values

        if not header and 'FoamFile' in values:
            del(values['FoamFile'])

        return cls(of_filename, values, replace, time_range)

    @property
    def isSolutionParameter(self):
        """Return True."""
        return True

    @property
    def values(self):
        """Return OpenFOAM file name."""
        return self.__values

    @values.setter
    def values(self, v):
        assert isinstance(v, dict), 'values should be a dictionary not a {}.' \
            .format(type(v))
        self.__values = v

    @property
    def filename(self):
        """Return OpenFOAM file name."""
        return self.__filename

    @filename.setter
    def filename(self, f):
        assert f in self._of_filenames, '{} is not a valid OpenFOAM dictionary ' \
            'file. Try one of the files below:\n{}.' \
            .format(f, '\n'.join(self._of_filenames))

        self.__filename = f

    @property
    def time_range(self):
        """Get time range."""
        return (self.__t0, self.__t1)

    def is_time_in_range(self, time):
        """Check if time is in this SolutionParameter time range."""
        return self.__t0 <= float(time) < self.__t1

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        kv = '\n'.join('{}: {};'.format(k, v) for k, v in self.values.iteritems())
        return 'SolutionParameter::{}\n{}\n@{}'\
            .format(self.filename, kv, self.time_range)
