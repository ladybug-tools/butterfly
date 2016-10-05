# coding=utf-8
"""Butterfly Solution."""
from copy import deepcopy
from .helper import checkFiles
from .parser import CppDictParser


class Solution(object):
    """Butterfly Solution.

    This class creates a solution from a recipe which is ready to run and monitor.

    Args:
        recipe: A butterfly recipe.
    """

    def __init__(self, recipe, decomposeParDict=None):
        """Init solution."""
        self.__recipe = recipe
        self.__decomposeParDict = decomposeParDict
        self.__isRunStarted = False
        self.__isRunFinished = False
        self.__process = None
        self.__logFiles = None
        self.__errFiles = None

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

    def updateSolutionParams(self, solParams):
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
    """

    _OFFilenames = ('epsilon', 'k', 'nut', 'p', 'U', 'turbulenceProperties',
                    'transportProperties', 'blockMeshDict', 'controlDict',
                    'fvSchemes', 'fvSolution', 'snappyHexMeshDict', 'probes')

    def __init__(self, OFFilename, values, replace=False):
        """Create solution parameter."""
        self.filename = OFFilename
        self.values = values
        self.replace = replace

    @classmethod
    def fromDictionaryFile(cls, OFFilename, filepath, replace=False):
        """Create from an OpenFOAM dictionary file."""
        # convert values to python dictionary
        values = CppDictParser.fromFile(filepath).values
        return cls(OFFilename, values, replace)

    @classmethod
    def fromDictionary(cls, OFFilename, dictionary, replace=False):
        """Create from an OpenFOAM dictionary."""
        # convert values to python dictionary
        values = CppDictParser(text=dictionary).values
        return cls(OFFilename, values, replace)

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

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return 'SolutionParameter@{}'\
            .format('::'.join([self.filename] + self.values.keys()))
