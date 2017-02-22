# assign inputs
_nonOrthogonality = IN[0]
fvSchemes = None

try:
    from butterfly.fvSchemes import FvSchemes
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/dynamo/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if  _nonOrthogonality:
    fvSchemes = FvSchemes.fromMeshOrthogonality(_nonOrthogonality)


# assign outputs to OUT
OUT = (fvSchemes,)