# assign inputs
_solution, _name, _points, _field, _run = IN
probes = values = None


try:
    from butterfly.utilities import loadProbesFromPostProcessingFile
    from butterfly_dynamo.geometry import xyzToPoint, xyzToVector
    import butterfly_dynamo.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

import os


if _solution and _name and any(p is not None for p in _points) and _field and _run:
    
    assert hasattr(_solution, 'sample'), \
        'Invalid Input: <{}> is not a valid Butterfly Case or Solution.'.format(_solution)
    c = uc.convertDocumentUnitsToMeters()
    cr = 1.0 / c
    
    points = ((pt.X * c, pt.Y * c, pt.Z * c) for pt in _points)
    res = _solution.sample(_name, points, _field)
    
    if res:
        probes = (xyzToPoint(p, cr) for p in res.probes)
        
        if isinstance(res.values[0], float) == 1:
            values = res.values
        else:
            values = (xyzToVector(v) for v in res.values)

# assign outputs to OUT
OUT = probes, values