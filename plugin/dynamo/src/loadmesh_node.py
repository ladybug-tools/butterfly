# assign inputs
_case, innerMesh_, _load = IN
mesh = None

if _case and _load:
    mesh = _case.loadMesh(innerMesh_)

# assign outputs to OUT
OUT = (mesh,)