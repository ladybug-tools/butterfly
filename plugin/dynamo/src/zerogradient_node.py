# assign inputs

zeroGradient = None

try:
    from butterfly.fields import ZeroGradient
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

zeroGradient = ZeroGradient()


# assign outputs to OUT
OUT = (zeroGradient,)