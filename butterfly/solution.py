# coding=utf-8
"""Butterfly Solution."""
from copy import deepcopy
from .helper import checkFiles


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

    def updateSolutionParams(self, simParams):
        """Update parameters."""
        if not simParams:
            # if input is None return
            return
        # check input with the current and update them if there has been changes
        if simParams.controlDict:
            # compare the values that can be modifed via interface
            # This can be written simply as self.controlDict != simParams.controlDict
            # once we can load OpenFOAM dictionaries into butterfly.
            _update = False
            if self.__recipe.case.controlDict.startTime != \
                    simParams.controlDict.startTime:
                _update = True
                self.__recipe.case.controlDict.startTime = \
                    simParams.controlDict.startTime

            if self.__recipe.case.controlDict.endTime != \
                    simParams.controlDict.endTime:
                _update = True
                self.__recipe.case.controlDict.endTime = \
                    simParams.controlDict.endTime

            if self.__recipe.case.controlDict.writeInterval != \
                    simParams.controlDict.writeInterval:
                _update = True
                self.__recipe.case.controlDict.writeInterval = \
                    simParams.controlDict.writeInterval

            if self.__recipe.case.controlDict.writeCompression != \
                    simParams.controlDict.writeCompression:
                _update = True
                self.__recipe.case.controlDict.writeCompression = \
                    simParams.controlDict.writeCompression

            if _update:
                print 'Updating controlDict...'
                self.controlDict.save(self.projectDir)

        if simParams.residualControl and \
                self.residualControl != simParams.residualControl:
                print 'Updating residualControl...'
                self.__recipe.case.fvSolution.residualControl = \
                    simParams.residualControl
                self.__recipe.case.fvSolution.save(self.projectDir)

        if simParams.probes and self.probes != simParams.probes:
            print 'Updating probes...'
            self.__recipe.case.probes = simParams.probes
            self.probes.save(self.projectDir)
            # just in case probes was not there and now should be included
            # in controlDict
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


class SolutionParameters(object):
    """A collection of parameters that can be adjusted in run-time.

    Attributes:
        controlDict: Control ditctionary.
        residualControl: Residual control values.
        probes: Butterfly probes.
    """

    def __init__(self, controlDict, residualControl, probes):
        """Initiate class."""
        self.controlDict = controlDict
        self.residualControl = residualControl
        self.probes = probes

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return self.__class__.__name__
