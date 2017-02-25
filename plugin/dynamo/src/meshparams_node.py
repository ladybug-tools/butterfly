# assign inputs
_cellSizeXYZ_, _gradXYZ_, _locationInMesh_, _globRefineLevel_ = IN
meshParams = None

try:
    # import butterfly
    from butterfly.meshingparameters import MeshingParameters
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

# create blockMeshDict based on BBox
if _gradXYZ_:
    _gradXYZ_ = _gradXYZ_.X, _gradXYZ_.Y, _gradXYZ_.Z

meshParams = MeshingParameters(
    _cellSizeXYZ_, _gradXYZ_, _locationInMesh_, _globRefineLevel_)

# assign outputs to OUT
OUT = (meshParams,)