# assign inputs
_points, _fields_, _writeInterval_ = IN
probes = None

try:
    from butterfly.functions import Probes
    import butterfly_dynamo.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _points:
    probes = Probes()
    c = uc.convertDocumentUnitsToMeters()
    probes.probeLocations = ((p.X * c, p.Y * c, p.Z * c) for p in _points)
    probes.fields = _fields_
    probes.writeInterval = _writeInterval_

# assign outputs to OUT
OUT = (probes,)