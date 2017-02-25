# assign inputs
_quality = IN[0]
divSchemes = None

try:
    from butterfly.fvSchemes import FvSchemes
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _quality is not None:
    divSchemes = FvSchemes.divSchemesCollector[_quality%2]


# assign outputs to OUT
OUT = (divSchemes,)