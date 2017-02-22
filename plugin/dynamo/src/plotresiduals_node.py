# assign inputs
_solution, _fields_, timeRange_, _load = IN
timeRange = fields = values = None

try:
    import butterfly
    from butterfly.parser import ResidualParser
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/dynamo/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


if _solution and _load:
    
    assert hasattr(_solution, 'residualFile'), \
        '{} is not a valid Solution.'.format(_solution)
    
    p = ResidualParser(_solution.residualFile)
    
    if not _fields_:
        try:
            fields = _solution.residualFields
        except:
            raise ValueError('Failed to load fields from solution {}.'.format(_solution))
    else:
        fields = _fields_
    
    timeRange = '{} To {}'.format(*p.timeRange)

    values = tuple(
        tuple(float(i) for i in p.getResiduals(field, timeRange_))
        for field in fields)

    

# assign outputs to OUT
OUT = timeRange, fields, values