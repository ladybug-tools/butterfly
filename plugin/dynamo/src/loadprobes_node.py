# assign inputs
_solution, _field = IN
probes = None

try:
    from butterfly.utilities import loadProbesFromPostProcessingFile
    from butterfly_dynamo.geometry import xyzToPoint
    import butterfly_dynamo.unitconversion as uc
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
        rawValues = loadProbesFromPostProcessingFile(probesDir, _field)
    else:
        assert hasattr(_solution, 'loadProbes'), \
            'Invalid Input: <{}> is not a valid Butterfly Solution.'.format(_solution)
        try:
            rawValues = _solution.loadProbes(_field)
        except Exception as e:
            raise ValueError('Failed to load probes:\n\t{}'.format(e))
    
    c = 1.0 / uc.convertDocumentUnitsToMeters()
    try:
        probes = tuple(xyzToPoint(v, c) for v in rawValues)
    except:
        probes = rawValues

# assign outputs to OUT
OUT = (probes,)