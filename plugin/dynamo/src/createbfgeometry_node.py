# assign inputs
_name, _geo, _boundary_, refineLevels_, nSrfLayers_, _meshSet_ = IN
BFGeometries = None

try:
    from butterfly_dynamo.geometry import BFGeometryDS
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _geo and _name:
    BFGeometries = BFGeometryDS(_name, _geo, _boundary_, refineLevels_, nSrfLayers_, _meshSet_)

# assign outputs to OUT
OUT = (BFGeometries,)