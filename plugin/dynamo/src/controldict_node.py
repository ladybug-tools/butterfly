# assign inputs
_startTime_, _endTime_, _writeInterval_, _writeCompression_, funcObjects_ = IN
controlDict = None

try:
    from butterfly.controlDict import ControlDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


cd = ControlDict()
if _startTime_ is not None:
    cd.startTime = _startTime_

if _endTime_ is not None:
    cd.endTime = _endTime_

if _writeInterval_ is not None:
    cd.writeInterval = _writeInterval_

if _writeCompression_ is not None:
    cd.writeCompression = _writeCompression_

if funcObjects_ and funcObjects_[0] is not None:
    cd.functions = funcObjects_

controlDict = cd

# assign outputs to OUT
OUT = (controlDict,)