# assign inputs
name_, _folder, _run = IN
case = None

try:
    from butterfly_dynamo.case import Case
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/dynamo/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _folder and _run: 
    # create OpenFoam Case
    case = Case.fromFolder(_folder, name_)
    case.save(overwrite=False)

# assign outputs to OUT
OUT = (case,)