# assign inputs
_windwardX_, _topX_, _sidesX_, _leewardX_ = IN
tunnelParams = None

try:
    from butterfly.windtunnel import TunnelParameters
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

tunnelParams = TunnelParameters(_windwardX_, _topX_, _sidesX_, _leewardX_)

# assign outputs to OUT
OUT = (tunnelParams,)