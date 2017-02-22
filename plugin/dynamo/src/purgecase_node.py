# assign inputs
_case, _blockMesh_, _snappyHexMesh_, _results_, _postProcessing_ = IN
 = None

if _case:
    _case.purge(_blockMesh_, _snappyHexMesh_, _results_, _postProcessing_)
else:
    print "_case input is empty."

# assign outputs to OUT
OUT = 