"""Butterfly Solution."""


class Solution(object):
    """Butterfly Solution.

    This class creates a solution from a recipe which is ready to run and monitor.

    Args:
        recipe: A butterfly recipe.
    """

    def __init__(self, recipe):
        """Init solution."""
        self.__recipe = recipe
        self.__isRunStarted = False
        self.__isRunFinished = False
        self.__process = None

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
    def logFile(self):
        """Get full path to log file."""
        return self.__recipe.logFile

    @property
    def log(self):
        """Get the log report."""
        try:
            with open(self.logFile, 'rb') as log:
                return ' '.join(log.readlines())
        except Exception as e:
            return 'Failed to load the log file:\n{}'.format(e)

    @property
    def errFile(self):
        """Get full path to error file."""
        return self.__recipe.errFile

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
            with open(self.errFile, 'rb') as log:
                _err = ' '.join(log.readlines())
                if len(_err) > 0:
                    raise Exception(_err)
            return False

    def updateSolutionParams(self, simParams):
        """Update parameters."""
        if not simParams:
            # if input is None return
            return
        # check input with the current and update them if there has been changes
        if simParams.controlDict and self.controlDict != simParams.controlDict:
            print 'Updating controlDict...'
            self.__recipe.case.controlDict.startTime = \
                simParams.controlDict.startTime
            self.__recipe.case.controlDict.endTime = \
                simParams.controlDict.endTime
            self.__recipe.case.controlDict.writeInterval = \
                simParams.controlDict.writeInterval
            self.__recipe.case.controlDict.writeCompression = \
                simParams.controlDict.writeCompression

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
        log = self.recipe.run(wait=False)
        self.__process = log.process
        self.__isRunStarted = True
        self.__isRunFinished = False

    def terminate(self):
        """Cancel the solution."""
        self.__process.terminate()

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

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return self.__class__.__name__
