# assign inputs
_numOfCpus_ = IN[0]
decomposeParDict = None

try:
    from butterfly.decomposeParDict import DecomposeParDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


try:
    numberOfSubdomains = int(_numOfCpus_)
except:
    numberOfSubdomains = 2

decomposeParDict = DecomposeParDict.scotch(numberOfSubdomains)

# assign outputs to OUT
OUT = (decomposeParDict,)