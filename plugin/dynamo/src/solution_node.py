# assign inputs
_case, _recipe, decomposeParDict_, solutionParams_, _write, run_ = IN
solution = timestep = residualFields = residualValues = logFiles = None

import os

try:
    from butterfly.solution import Solution
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
        '\nYou can download butterfly from package manager.' + \
        '\nOpen an issue on github if you think this is a bug:' + \
        ' https://github.com/ladybug-analysis-tools/butterfly/issues'

    raise ImportError('{}\n{}'.format(msg, e))


if _case and _recipe and _write:
    # create a new one and copy
    solution = Solution(_case, _recipe, decomposeParDict_, solutionParams_)
    residualFields = solution.residualFields

    timestep = solution.timestep
    solution.updateSolutionParams(solutionParams_, timestep)

    # wait for the run to be done
    if run_:
        solution.run(wait=True)
        residualFields = solution.residualFields
        info = solution.info
        timestep = info.timestep
        residualValues = info.residualValues
        solution.terminate()  # in case user closes batch file
        logFiles = solution.logFiles or os.path.join(_case.projectDir, _recipe.logFile)

# assign outputs to OUT
OUT = solution, timestep, residualFields, residualValues, logFiles
