# assign inputs
_solution, _field = IN
values = None

try:
    from butterfly.utilities import loadProbeValuesFromFolder
    from butterfly_dynamo.geometry import xyzToVector
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

import os


if _solution and _field:
    if isinstance(_solution, str):
        projectDir = _solution.replace('\\\\','/').replace('\\','/')
        probesDir = os.path.join(projectDir, 'postProcessing\\probes') 
        rawValues = loadProbeValuesFromFolder(probesDir, _field)
    else:
        assert hasattr(_solution, 'loadProbeValues'), \
            'Invalid Input: <{}> is not a valid Butterfly Solution.'.format(_solution)
        try:
            rawValues = _solution.loadProbeValues(_field)
        except Exception as e:
            raise ValueError('Failed to load values:\n\t{}'.format(e))
            
    try:
        values = tuple(xyzToVector(v) for v in rawValues)
    except:
        values = rawValues

# assign outputs to OUT
OUT = (values,)