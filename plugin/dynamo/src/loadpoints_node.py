# assign inputs
_case, _load = IN
pts = None

if _case and _load:
    pts = _case.loadPoints()

# assign outputs to OUT
OUT = (pts,)