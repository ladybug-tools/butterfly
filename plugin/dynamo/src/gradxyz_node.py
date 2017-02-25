# assign inputs
_xGrading_, _yGrading_, _zGrading_ = IN
gradXYZ = None

try:
    from butterfly.grading import SimpleGrading
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

gradXYZ = SimpleGrading(_xGrading_, _yGrading_, _zGrading_)

# assign outputs to OUT
OUT = (gradXYZ,)