# coding=utf-8
"""Butterfly Solution."""
from copy import deepcopy
from collections import namedtuple, OrderedDict
import os

from .utilities import tail, loadSkippedProbes
from .parser import CppDictParser


class Solution(object):
    """Butterfly Solution.

    This class creates a solution from a recipe which is ready to run and monitor.

    Args:
        case: A butterfly case.
        recipe: A butterfly recipe.
        decomposeParDict: decomposeParDict for parallel run (default: None).
        solutionParameter: A solutionParameter (default: None).
        removeExtraFoamFiles: set to True if you want butterfly to remove all the
            extra files in 0 folder once you update the recipe (default: False).
    """

    def __init__(self, case, recipe, decomposeParDict=None, solutionParameter=None,
                 removeExtraFoamFiles=False):
        """Init solution."""
        self.__remove = removeExtraFoamFiles
        assert hasattr(case, 'isCase'), \
            'ValueError:: {} is not a Butterfly.Case'.format(case)
        self.decomposeParDict = decomposeParDict

        self.__case = case
        self.case.decomposeParDict = self.decomposeParDict

        self.recipe = recipe
        self.updateSolutionParams(solutionParameter)
        # set internal properties for running the solution

        # place holder for residuals
        self.__residualValues = OrderedDict.fromkeys(self.residualFields, 0)
        self.__isRunStarted = False
        self.__isRunFinished = False
        self.__process = None
        self.__logFiles = None
        self.__errFiles = None

    @property
    def projectName(self):
        """Get porject name."""
        return self.case.projectName

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
        self.__recipe.prepareCase(self.case, overwrite=True,
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
    def removeExtraFoamFiles(self):
        """If True, solution will remove extra files everytime recipe changes."""
        return self.__remove

    @property
    def projectDir(self):
        """Get project directory."""
        return self.case.projectDir

    @property
    def residualFields(self):
        """Get list of residuals to be watched during the run."""
        return self.recipe.residualFields

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
    def residualFile(self):
        """Return address of the residual file."""
        return os.path.join(self.case.logFolder, self.recipe.logFile)

    @property
    def logFiles(self):
        """Get full path to log files."""
        return self.__logFiles

    @property
    def log(self):
        """Get the log report."""
        isContent, content = self.case.runmanager.checkFileContents(self.logFiles)

    @property
    def errFiles(self):
        """Get full path to error files."""
        return self.__errFiles

    @property
    def isRunning(self):
        """Check if the solution is still running."""
        if not self.__isRunStarted and not self.__isRunFinished:
            return False
        elif self.__process.poll() is None:
            return True
        else:
            self.__isRunFinished = True
            self.case.renameSnappyHexMeshFolders()
            # load errors if any
            self.case.runmanager.checkFileContents(self.logFiles)
            failed, err = self.case.runmanager.checkFileContents(self.errFiles)

            assert not failed, err

    @property
    def timestep(self):
        """Get latest timestep for this solution."""
        return self.__getLatestTime()

    @property
    def residualValues(self, latestTime=True):
        """Get timestep and residual values as a tuple."""
        if latestTime:
            return self.__getInfo().residualValues
        else:
            raise NotImplementedError()

    @property
    def info(self):
        """Get timestep and residual values as a tuple."""
        return self.__getInfo()

    def __getInfo(self):
        i = namedtuple('Info', 'timestep residualValues')
        # get end of the log file
        if not os.path.isfile(self.residualFile):
            return i(0, self.__residualValues.values())

        text = tail(self.residualFile).split("\nTime =")[-1].split('\n')
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

    def __getLatestTime(self):
        # get end of the log file
        if not os.path.isfile(self.residualFile):
            return 0
        text = tail(self.residualFile).split("\nTime =")[-1].split('\n')
        # get timestep
        try:
            t = int(text[0])
        except ValueError:
            t = 0
        return t

    def updateFromRecipe(self, recipe):
        """Update solution from recipe inputs.

        This method creates a SolutionParameter from each recipe property, and
        uses updateSolutionParams to update the solution.
        """
        tp = SolutionParameter.fromCppDictionary('turbulenceProperties',
                                                 str(recipe.turbulenceProperties))
        fvSc = SolutionParameter.fromCppDictionary('fvSchemes',
                                                   str(recipe.fvSchemes))
        fvSol = SolutionParameter.fromCppDictionary('fvSolution',
                                                    str(recipe.fvSolution))

        self.updateSolutionParams((tp, fvSc, fvSol))

    def updateSolutionParams(self, solParams, timestep=None):
        """Update parameters.

        Attributes:
            solParams: A list of solution parameters.
        """
        if not solParams:
            # if input is None return
            return
        # check input with the current and update them if there has been changes
        for solPar in solParams:
            assert hasattr(solPar, 'isSolutionParameter'), \
                '{} is not a solution parameter.'.format(solPar)

            # check if this timestep in range of SolutionParameter time range
            if timestep is not None and not solPar.isTimeInRange(timestep):
                # not in time range! try the next one
                continue

            try:
                update = getattr(self.__case, solPar.filename) \
                    .updateValues(solPar.values, solPar.replace)
            except AttributeError as e:
                # probes can be empty at start
                raise AttributeError(e)

            # check to remove functions if needed
            if solPar.filename == 'controlDict':
                curFunc = self.__case.controlDict.values['functions'].keys()
                newFunc = solPar.values['functions'].keys()

                for k in curFunc:
                    if k not in newFunc:
                        del(self.__case.controlDict.values['functions'][k])
                        update = True

            if update:
                print('Updating {}...'.format(solPar.filename))
                ffile = getattr(self.__case, solPar.filename)
                ffile.save(self.projectDir)

                # just in case probes was not there and now should be included
                # in controlDict
                if solPar.filename == 'probes':
                    if not self.controlDict.include:
                        self.controlDict.include = solPar.filename
                        self.controlDict.save(self.projectDir)

    def run(self, wait=False):
        """Execute the solution."""
        self.case.renameSnappyHexMeshFolders()
        log = self.case.command(
            cmd=self.recipe.application,
            args=None,
            decomposeParDict=self.__decomposeParDict,
            run=True, wait=wait)
        self.__process = log.process
        self.__errFiles = log.errorfiles
        self.__logFiles = log.logfiles
        self.__isRunStarted = True
        if not wait:
            self.__isRunFinished = False
        else:
            self.__isRunFinished = True

    def purge(self, removePolyMeshContent=True,
              removeSnappyHexMeshFolders=True,
              removeResultFolders=False,
              removePostProcessingFolder=False):
        """Purge solution's case folder."""
        self.case.purge(
            removePolyMeshContent, removeSnappyHexMeshFolders,
            removeResultFolders, removePostProcessingFolder)

    def terminate(self):
        """Cancel the solution."""
        self.case.runmanager.terminate()
        if self.decomposeParDict:
            # remove processor folders if they haven't been removed already.
            self.case.removeProcessorFolders()

    def loadProbeValues(self, field):
        """Return OpenFOAM probes results for a given field (e.g. U)."""
        return self.case.loadProbeValues(field)

    def loadProbes(self, field):
        """Return OpenFOAM probes location for a given field (e.g. U)."""
        return self.case.loadProbes(field)

    def skippedProbes(self):
        """Get list of probes that are skipped from the solution."""
        return loadSkippedProbes(os.path.join(self.case.logFolder,
                                              self.recipe.logFile))

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
        return "{}::{}".format(self.projectName, self.recipe)


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
        timeRange: Time range that this SolutioParameter is valid as a tuple
            (default: (0, 1.0e+100)).
    """

    _OFFilenames = ('epsilon', 'k', 'nut', 'p', 'U', 'T', 'turbulenceProperties',
                    'transportProperties', 'blockMeshDict', 'controlDict',
                    'fvSchemes', 'fvSolution', 'snappyHexMeshDict', 'probes')

    def __init__(self, OFFilename, values, replace=False, timeRange=None):
        """Create solution parameter."""
        self.filename = OFFilename
        self.values = values
        self.replace = replace

        try:
            self.__t0 = int(timeRange[0])
            self.__t1 = int(timeRange[1])
        except TypeError:
            self.__t0, self.__t1 = 0, 1.0e+100
        except ValueError:
            self.__t0, self.__t1 = 0, 1.0e+100

    @classmethod
    def fromDictionaryFile(cls, OFFilename, filepath, replace=False,
                           timeRange=None):
        """Create from an OpenFOAM dictionary file."""
        # convert values to python dictionary
        values = CppDictParser.fromFile(filepath).values
        return cls(OFFilename, values, replace, timeRange)

    @classmethod
    def fromCppDictionary(cls, OFFilename, dictionary, replace=False,
                          timeRange=None, header=False):
        """Create from an OpenFOAM dictionary in text format."""
        # convert values to python dictionary
        values = CppDictParser(text=dictionary).values

        if not header and 'FoamFile' in values:
            del(values['FoamFile'])

        return cls(OFFilename, values, replace, timeRange)

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
        assert f in self._OFFilenames, '{} is not a valid OpenFOAM dictionary ' \
            'file. Try one of the files below:\n{}.' \
            .format(f, '\n'.join(self._OFFilenames))

        self.__filename = f

    @property
    def timeRange(self):
        """Get time range."""
        return (self.__t0, self.__t1)

    def isTimeInRange(self, time):
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
            .format(self.filename, kv, self.timeRange)
