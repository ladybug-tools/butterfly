# assign inputs
_RASModel_, _turbulence_, _printCoeffs_ = IN
RAS = None

try:
    from butterfly.turbulenceProperties import TurbulenceProperties
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


RAS = TurbulenceProperties.RAS(_RASModel_, _turbulence_, _printCoeffs_)

# assign outputs to OUT
OUT = (RAS,)