# coding=utf-8
"""Butterfly Solution."""
from copy import deepcopy
from collections import namedtuple, OrderedDict
import os
from .helper import checkFiles, tail
from .parser import CppDictParser


class Solution(object):
    """Butterfly Solution.

    This class creates a solution from a recipe which is ready to run and monitor.

    Args:
        recipe: A butterfly recipe.
        decomposeParDict: decomposeParDict for parallel run.
        quantities: A list of quantities to be watched during the run.
    """

    def __init__(self, recipe, decomposeParDict=None, quantities=None):
        """Init solution."""
        self.__recipe = recipe
        self.__decomposeParDict = decomposeParDict
        self.__isRunStarted = False
        self.__isRunFinished = False
        self.__process = None
        self.__logFiles = None
        self.__errFiles = None
        self.quantities = quantities

    @property
    def projectName(self):
        """Get porject name."""
        return self.recipe.case.projectName

    @property
    def recipe(self):
        """Get recipe."""
        return self.__recipe

    @property
    def projectDir(self):
        """Get project directory."""
        return self.recipe.case.projectDir

    @property
    def quantities(self):
        """Get list of quantities to be watched during the run."""
        return self.__quantities

    @quantities.setter
    def quantities(self, q):
        if not q:
            self.__quantities = self.__recipe.quantities
        else:
            try:
                self.__quantities = tuple(q)
            except Exception as e:
                print "Failed to set quantities!\n{}".format(e)
                self.__quantities = self.__recipe.quantities

        # place holder for residuals
        self.__residualValues = OrderedDict.fromkeys(self.__quantities, 0)

    @property
    def controlDict(self):
        """Get controlDict."""
        return self.__recipe.case.controlDict

    @property
    def residualControl(self):
        """Get residualControl values for this solution."""
        return self.__recipe.case.fvSolution.residualControl

    @property
    def probes(self):
        """Get probes if any."""
        return self.__recipe.case.probes

    @property
    def residualFile(self):
        """Return address of the residual file."""
        return self.__recipe.residualFile

    @property
    def logFiles(self):
        """Get full path to log files."""
        return self.__logFiles

    @property
    def log(self):
        """Get the log report."""
        isContent, content = checkFiles(self.logFiles)

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
            self.recipe.case.renameSnappyHexMeshFolders()
            # load errors if any
            checkFiles(self.logFiles)
            failed, err = checkFiles(self.errFiles)

            assert not failed, err

    @property
    def timestep(self):
        """Get latest timestep for this solution."""
        return self.__getLatestTime()

    @property
    def residualValues(self, latestTime=True):
        """Get timestep and residual values as a tuple."""
        if latestTime:
            return self.__getInfo().residuals
        else:
            raise NotImplementedError()

    @property
    def info(self):
        """Get timestep and residual values as a tuple."""
        return self.__getInfo()

    def __getInfo(self):
        i = namedtuple('Info', 'timestep residuals')
        # get end of the log file
        if not os.path.isfile(self.residualFile):
            return i(0, self.__residualValues.values())

        text = tail(self.residualFile).split("\nTime =")[-1].split('\n')
        # get timestep
        try:
            t = int(text[0])
        except:
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
        except:
            t = 0
        return t

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
                update = getattr(self.__recipe.case, solPar.filename) \
                    .updateValues(solPar.values, solPar.replace)
            except AttributeError as e:
                # probes can be empty at start
                raise AttributeError(e)

            if update:
                print 'Updating {}...'.format(solPar.filename)
                ffile = getattr(self.__recipe.case, solPar.filename)
                ffile.save(self.projectDir)

                # This is not as simple as copying files!
                # if ffile.isZeroFile:
                #     # save file to processors folders if any
                #     if self.__decomposeParDict:
                #         for n in self.__decomposeParDict.numberOfSubdomains:
                #             _p = os.path.join(self.projectDir, 'processer%d' % n)
                #             if os.path.isdir(_p):
                #                 ffile.save(_p)

                # just in case probes was not there and now should be included
                # in controlDict
                if solPar.filename == 'probes':
                    if not self.controlDict.include:
                        self.controlDict.include = solPar.filename
                        self.controlDict.save(self.projectDir)

    def run(self):
        """Execute the solution."""
        self.recipe.case.renameSnappyHexMeshFolders()
        log = self.recipe.run(decomposeParDict=self.__decomposeParDict,
                              wait=False)
        self.__process = log.process
        self.__errFiles = log.errorfiles
        self.__logFiles = log.logfiles
        self.__isRunStarted = True
        self.__isRunFinished = False

    def terminate(self):
        """Cancel the solution."""
        self.__process.terminate()

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Solution representation."""
        return "{}::{}".format(self.recipe.case.projectName, self.recipe)


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

    _OFFilenames = ('epsilon', 'k', 'nut', 'p', 'U', 'turbulenceProperties',
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
        except:
            self.__t0, self.__t1 = 0, 1.0e+100

    @classmethod
    def fromDictionaryFile(cls, OFFilename, filepath, replace=False,
                           timeRange=None):
        """Create from an OpenFOAM dictionary file."""
        # convert values to python dictionary
        values = CppDictParser.fromFile(filepath).values
        return cls(OFFilename, values, replace, timeRange)

    @classmethod
    def fromDictionary(cls, OFFilename, dictionary, replace=False,
                       timeRange=None):
        """Create from an OpenFOAM dictionary."""
        # convert values to python dictionary
        values = CppDictParser(text=dictionary).values
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
        return 'SolutionParameter::{}@{}'\
            .format('.'.join([self.filename] + self.values.keys()),
                    self.timeRange)
