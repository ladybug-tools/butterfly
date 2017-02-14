# assign inputs
_case, _points, xAxis_, _run = IN
case = None
if _run and _case and any(p is not None for p in _points) and xAxis_:
    
    _case.blockMeshDict.updateVertices(
        tuple((p.X, p.Y, p.Z) for p in _points), (xAxis_.X, xAxis_.Y, xAxis_.Z))
    _case.blockMeshDict.save(_case.projectDir)
    case = _case

# assign outputs to OUT
OUT = (case,)