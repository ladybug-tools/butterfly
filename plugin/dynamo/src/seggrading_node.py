# assign inputs
_percentageLength, _percentageCells, _expansionRatio_ = IN
segmentGrading = None

try:
    from butterfly.grading import Grading
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/dynamo/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _percentageLength and _percentageCells:
    segmentGrading = Grading(_percentageLength, _percentageCells, _expansionRatio_)

# assign outputs to OUT
OUT = (segmentGrading,)